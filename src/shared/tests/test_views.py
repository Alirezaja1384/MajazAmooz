from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse
from django.views.generic import View
from django.db.models import CharField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from shared.views import (
    LogoutRequiredMixin,
    DynamicModelFieldDetailView,
    DeleteDeactivationView,
)

User = get_user_model()


@override_settings(LOGOUT_REQUIRED_URL="/auth/logout_required")
class LogoutRequiredMixinTest(TestCase):
    class LogoutNeededView(LogoutRequiredMixin, View):
        def get(self, request):
            return HttpResponse(status=200)

    def setUp(self):
        self.factory = RequestFactory()
        self.view = self.LogoutNeededView.as_view()
        self.user = User.objects.create(username="testuser")

    def test_logged_in_user(self):
        """
        Should redirect logged-in user.
        """
        request = self.factory.get("/logout_needed/")
        # Simulate logged-in user
        request.user = self.user

        response = self.view(request)
        self.assertRedirects(
            response,
            "/auth/logout_required?next=" + request.path,
            fetch_redirect_response=False,
        )

    def test_anonymous_user(self):
        """
        Should not redirect anonymous user.
        """
        request = self.factory.get("/logout_needed/")
        request.user = AnonymousUser()

        response = self.view(request)
        # Should not redirect user
        self.assertEqual(response.status_code, 200)

    def test_next_url_parameter(self):
        """
        Should not redirect if next parameter specified in url
        even if user is authenticated.
        """
        request = self.factory.get("/logout_needed/?next=/user/")
        request.user = self.user

        response = self.view(request)
        self.assertEqual(response.status_code, 200)


class DynamicModelFieldDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="user")

    def test_raise_improperly_configured(self):
        """If at least one of fields field doesn't have proper handler,
        it should raise ImproperlyConfigured error.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            model = User
            visible_field_types = {}

        view = DynamicDetailView()

        self.assertRaises(
            ImproperlyConfigured,
            view.get_model_field_value,
            self.user,
            self.user._meta.get_field("username"),
        )

    def test_use_simple_handler_should_not_raise(self):
        """If at least one of fields doesn't have proper handler and
        unimplemented_types_use_simple_handler set to True,
        it should not raise ImproperlyConfigured error and use
        simple handler by default.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            model = User
            visible_field_types = []
            unimplemented_types_use_simple_handler = True

        view = DynamicDetailView.as_view()
        request = self.factory.get("/dynamic_details/")

        self.assertEqual(view(request, pk=self.user.pk).status_code, 200)

    def test_context_fields_name(self):
        """get_context_name should use context_fields_name as key for
        fields name-value result in context.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            model = User
            # context_fields_name should not set to 'fields',
            # otherwise this test will fail.
            context_fields_name = "customized_context"
            visible_field_types = []
            unimplemented_types_use_simple_handler = True

        view = DynamicDetailView.as_view()
        request = self.factory.get("/dynamic_details/")
        context = view(request, pk=self.user.pk).context_data

        # Context should have customized context name
        self.assertIn(DynamicDetailView.context_fields_name, context)
        # And should not have default context name
        self.assertNotIn(
            DynamicModelFieldDetailView.context_fields_name, context
        )

    def test_get_default_fields(self):
        """If unimplemented_types_use_simple_handler set True,
        get_default_fields should return all of model fields.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            model = User
            visible_field_types = []
            unimplemented_types_use_simple_handler = True

        view = DynamicDetailView()
        view.object = self.user

        default_field_names = view.get_default_fields()
        model_field_names = [
            field.name for field in self.user._meta.get_fields()
        ]

        self.assertEqual(default_field_names, model_field_names)

    def test_exclude_fields_get_default_fields(self):
        """get_default_fields should not use fields in exclude_fields."""

        class DynamicDetailView(DynamicModelFieldDetailView):
            model = User
            exclude_fields = (
                "id",
                "username",
                "email",
            )
            visible_field_types = []
            unimplemented_types_use_simple_handler = True

        view = DynamicDetailView()
        view.object = self.user

        default_field_names = view.get_default_fields()
        self.assertNotIn(DynamicDetailView.exclude_fields, default_field_names)

    def test_get_model_field_value_use_custom_handler(self):
        """get_model_field_value should use specified handler
        in visible_field_types.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            def _custom_handler(obj, field):
                # Returns upper-case field value
                return str(getattr(obj, field.name)).upper()

            model = User
            fields = ("username",)
            visible_field_types = [
                {
                    "types": (CharField,),
                    "handler": _custom_handler,
                }
            ]

        view = DynamicDetailView()
        username = view.get_model_field_value(
            self.user, self.user._meta.get_field("username")
        )

        # result should be upper-case
        self.assertTrue(username.isupper())

    def test_get_additional_field_value_bound_method(self):
        """get_additional_field_value should not pass 'self'
        for bound methods.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            def hello(self):
                return "Hello!"

            model = User
            additional_content = (hello,)
            fields = (hello,)

        view = DynamicDetailView()
        # view.hello is a bound method
        additional_value = view.get_additional_field_value(view.hello)

        self.assertEqual(additional_value, view.hello())

    def test_get_additional_field_value_unbound_method(self):
        """get_additional_field_value should pass 'self'
        for unbound methods.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            def hello(self):
                return "Hello!"

            model = User
            additional_content = (hello,)
            fields = (hello,)

        view = DynamicDetailView()
        # view.fields[0] is an unbound method
        additional_value = view.get_additional_field_value(view.fields[0])

        self.assertEqual(additional_value, view.hello())

    def test_additional_field_short_description(self):
        """DynamicModelFieldDetailView should use additional_content's
        short_description as field name.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            def hello(self):
                return "Hello!"

            hello.short_description = "Says hello!"

            model = User
            additional_content = (hello,)
            fields = (hello,)

        view = DynamicDetailView()
        name_values = view.get_name_values()

        self.assertEqual(
            name_values,
            [{"name": view.hello.short_description, "value": view.hello()}],
        )

    def test_get_name_values(self):
        """get_name_values should return name and value of fields correctly.

        It should handle model fields by their own handler
        and additional contents by calling them.
        """

        class DynamicDetailView(DynamicModelFieldDetailView):
            def _custom_handler(obj, field):
                # Returns upper-case field value
                return str(getattr(obj, field.name)).upper()

            def hello(self):
                return "Hello!"

            hello.short_description = "Says hello!"

            visible_field_types = [
                {
                    "types": (CharField,),
                    "handler": _custom_handler,
                }
            ]

            model = User
            additional_content = (hello,)
            fields = (
                hello,
                "username",
                "email",
            )

        view = DynamicDetailView()
        view.object = self.user

        result = view.get_name_values()
        expected_result = [
            {"name": view.hello.short_description, "value": view.hello()},
            {
                "name": view.object._meta.get_field("username").verbose_name,
                "value": view.object.username.upper(),
            },
            {
                "name": view.object._meta.get_field("email").verbose_name,
                "value": view.object.email.upper(),
            },
        ]

        self.assertEqual(result, expected_result)


class DeleteDeactivationViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="testuser")

    class DeleteDeactivateUser(DeleteDeactivationView):
        model = User
        send_message = False
        success_url = "/successful_delete/"
        context_action_form_name = "available_actions"

    def test_context_form(self):
        """view's context_action_form_name should be a key in context
        and form should be an instance of view's form.
        """
        view = self.DeleteDeactivateUser.as_view()
        request = self.factory.get("/delete_user/")
        context = view(request, pk=self.user.pk).context_data

        self.assertIn(
            self.DeleteDeactivateUser.context_action_form_name, context
        )
        self.assertIsInstance(
            context[self.DeleteDeactivateUser.context_action_form_name],
            self.DeleteDeactivateUser.form,
        )

    def test_deactivate_object(self):
        """DeleteDeactivationView should redirect to success url
        and deactivate user
        """
        view = self.DeleteDeactivateUser.as_view()

        action = self.DeleteDeactivateUser.form.DEACTIVATE
        request = self.factory.post(
            "/delete_user/?id={self.user.pk}",
            data={"action": action},
        )
        response = view(request, pk=self.user.pk)

        # Update user from db
        self.user = User.objects.get(pk=self.user.pk)

        self.assertRedirects(
            response,
            self.DeleteDeactivateUser.success_url,
            fetch_redirect_response=False,
        )

        self.assertEqual(self.user.is_active, False)

    def test_delete_object(self):
        """DeleteDeactivationView should redirect to success url
        and user should not exist in database (should be deleted).
        """
        view = self.DeleteDeactivateUser.as_view()

        action = self.DeleteDeactivateUser.form.DELETE
        request = self.factory.post(
            "/delete_user/?id={self.user.pk}",
            data={"action": action},
        )
        response = view(request, pk=self.user.pk)

        self.assertRedirects(
            response,
            self.DeleteDeactivateUser.success_url,
            fetch_redirect_response=False,
        )

        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_custom_deactivation_field_value(self):
        """DeleteDeactivationView should use model_deactivation_value
        as model_deactivation_field's value on deactivation.
        """

        class CustomDeactivationFieldNameValue(DeleteDeactivationView):
            model = User
            send_message = False
            success_url = "/successful_delete/"

            model_deactivation_field = "first_name"
            model_deactivation_value = "DEACTIVATE_USER"

        action = CustomDeactivationFieldNameValue.form.DEACTIVATE
        request = self.factory.post(
            "/delete_user/?id={self.user.pk}",
            data={"action": action},
        )
        CustomDeactivationFieldNameValue.as_view()(request, pk=self.user.pk)

        # Update user from db
        self.user = User.objects.get(pk=self.user.pk)

        self.assertEqual(
            getattr(
                self.user,
                CustomDeactivationFieldNameValue.model_deactivation_field,
            ),
            CustomDeactivationFieldNameValue.model_deactivation_value,
        )
