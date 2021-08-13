from http import HTTPStatus
from unittest import mock
from model_bakery import baker
from django.http import HttpResponse
from django.db import DatabaseError, models
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from shared.tests.utils import ModelTestCase
from ajax.views import shared as shared_views
from .utils import ajax_request

User = get_user_model()


@mock.patch.multiple(
    shared_views, logger=mock.DEFAULT, transaction=mock.DEFAULT
)
class AjaxViewTest(TestCase):
    class TestAjaxView(shared_views.AjaxView):
        def db_operation(self):
            return HttpResponse(status=200)

    class TestBrokenAjaxView(shared_views.AjaxView):
        db_error_default_text = "Default error text"

        def db_operation(self):
            raise DatabaseError

    def test_get_request_data(self, **_):
        """get_request_data should return sent data as dictionary."""
        data = {"key": "value"}

        view = self.TestAjaxView()
        view.setup(ajax_request(data))

        view_data = view.get_request_data()
        self.assertEqual(view_data, data)

    def test_non_ajax_request_status_bad_request(self, **_):
        """Should return BAD_REQUEST response (status code: 400)
        for non-ajax requests.
        """
        request = RequestFactory().post("/")
        view = self.TestAjaxView.as_view()

        self.assertEqual(view(request).status_code, HTTPStatus.BAD_REQUEST)

    def test_ajax_request_status_ok(self, **_):
        """Should return OK response (status code: 200) for ajax requests."""
        request = ajax_request()
        view = self.TestAjaxView.as_view()

        self.assertEqual(view(request).status_code, HTTPStatus.OK)

    def test_broken_db_operation_rollback(
        self, transaction: mock.MagicMock, **_
    ):
        """Should rollback database operation when db_operation()
        raises DatabaseError.

        Args:
            transaction (mock.MagicMock): Mocked transaction module.
        """
        self.TestBrokenAjaxView.as_view()(ajax_request())
        savepoint = transaction.savepoint.return_value

        transaction.rollback.assert_called_with(savepoint)

    def test_broken_log_error(self, logger: mock.MagicMock, **_):
        """Should log error when db_operation() raises DatabaseError.

        Args:
            logger (mock.MagicMock): Mocked logger variable.
        """
        self.TestBrokenAjaxView.as_view()(ajax_request())
        self.assertTrue(logger.error.called)

    def test_broken_response_error_status(self, **_):
        """Should return error status when db_operation() raises DatabaseError.
        Also should use db_error_default_text as error descreption.
        """
        response = self.TestBrokenAjaxView.as_view()(ajax_request())

        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {
                "status": shared_views.InsertOrDeleteStatus.ERROR,
                "error": self.TestBrokenAjaxView.db_error_default_text,
            },
        )


class AjaxModelCreateDeleteViewTest(ModelTestCase):
    class TestEmployeeCreateDeleteView(shared_views.AjaxModelCreateDeleteView):
        class TestEmployeeModel(models.Model):
            name = models.CharField(max_length=20)

        employee_name = None
        model = TestEmployeeModel

        def prepare_objects(self):
            self.employee_name = self.data.get("name")

        def get_objects(self):
            return self.model.objects.filter(name=self.employee_name)

        def create_object(self):
            self.model.objects.create(name=self.employee_name)

    model = TestEmployeeCreateDeleteView.TestEmployeeModel

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(User)
        cls.view = cls.TestEmployeeCreateDeleteView.as_view()

    def test_authentication_required(self):
        """Should not return OK status(200) when user is not authenticated."""
        response = self.view(ajax_request())
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_create_response_status(self):
        """Should response INSERTED as status when creates object."""
        request = ajax_request({"name": "John"}, self.user)

        self.assertJSONEqual(
            str(self.view(request).content, "utf8"),
            {"status": shared_views.InsertOrDeleteStatus.INSERTED},
        )

    def test_create_model_object(self):
        """Should create object when it doesn't exist in database."""
        self.view(ajax_request({"name": "John"}, self.user))
        self.assertTrue(self.model.objects.filter(name="John").exists())

    def test_delete_response_status(self):
        """Should response DELETED as status when deletes object."""
        self.model.objects.create(name="John")
        # Send request with existing name
        request = ajax_request({"name": "John"}, self.user)

        self.assertJSONEqual(
            str(self.view(request).content, "utf8"),
            {"status": shared_views.InsertOrDeleteStatus.DELETED},
        )

    def test_delete_model_object(self):
        """Should delete object when it exists in database."""
        employee = self.model.objects.create(name="John")
        # Send request with existing name
        self.view(ajax_request({"name": employee.name}, self.user))

        self.assertNotIn(employee, self.model.objects.all())
