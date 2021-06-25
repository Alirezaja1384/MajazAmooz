from datetime import date, datetime
from typing import TypedDict, Union, Callable, Optional
import bleach
from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponseBadRequest
from django.views.generic import DetailView, DeleteView
from django.utils.safestring import mark_safe
from django.utils.timezone import localdate, localtime
from django.core.exceptions import ImproperlyConfigured
from django.db.models import (
    Field,
    Model,
    QuerySet,
    CharField,
    TextField,
    BooleanField,
    IntegerField,
    ImageField,
    ManyToManyField,
    DateField,
    DateTimeField,
)
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django_bleach.models import BleachField
from django_bleach.utils import get_bleach_default_options
from shared.templatetags.image_utils import image_tag


class FieldNameValue(TypedDict):
    name: str
    value: str


class FieldValueHandlers:
    @staticmethod
    def simple_field_handler(obj: Model, field: Model) -> str:
        """handles BooleanField and its children

        Args:
            obj (Model): Model object.
            field (IntegerField): Models's field.

        Returns:
            str: String of field value.
        """
        return str(getattr(obj, field.name, ""))

    @staticmethod
    def boolean_field_handler(obj: Model, field: BooleanField) -> str:
        """handles BooleanField and its children

        Args:
            obj (Model): Model object.
            field (IntegerField): Models's field.

        Returns:
            str: If field's value is True returns 'بله'
                 else returns 'خیر'.
        """
        value = getattr(obj, field.name)
        return "بله" if value else "خیر"

    @staticmethod
    def integer_field_handler(obj: Model, field: IntegerField) -> str:
        """handles IntegerField and its children

        Args:
            obj (Model): Model object.
            field (IntegerField): Models's field.

        Returns:
            str: If field has choices returns choice display
                 else returns field value.
        """
        if field.choices:
            return getattr(obj, f"get_{field.name}_display")()
        else:
            return str(getattr(obj, field.name, ""))

    @staticmethod
    def bleach_field_handler(obj: Model, field: BleachField) -> str:
        """Handles BleachField

        Args:
            obj (Model): Model object.
            field (BleachField): Model's field.

        Returns:
            str: Allowed content as safe data
        """
        value = str(getattr(obj, field.name, ""))
        bleach_options = get_bleach_default_options()
        clean_value = bleach.clean(value, **bleach_options)
        return mark_safe(clean_value)

    @staticmethod
    def image_field_handler(obj: Model, field: ImageField) -> str:
        """Handles ImageField (returns an img tag of the image)

        Args:
            obj (Model): Model object.
            field (ImageField): Model's field.

        Returns:
            str: An img tag of the image
        """
        image: ImageField = getattr(obj, field.name)
        return image_tag(image=image, alt=str(obj))

    @staticmethod
    def many_to_many_field_handler(obj: Model, field: ManyToManyField) -> str:
        """Handles ManyToManyField

        Args:
            obj (Model): Model object.
            field (ManyToManyField): Model's field.

        Returns:
            str: str() related model objects
        """
        relation: QuerySet = getattr(obj, field.name).all()
        return "، ".join([str(item) for item in relation])

    @staticmethod
    def date_field_handler(obj: Model, field: DateField) -> date:
        """Handles DateField

        Args:
            obj (Model): Model object.
            field (DateField): Model's date field.

        Returns:
            date: localized date.
        """
        original: date = getattr(obj, field.name)
        localized: date = localdate(original)
        return localized

    @staticmethod
    def datetime_field_handler(obj: Model, field: DateTimeField) -> datetime:
        """Handles DateTimeField

        Args:
            obj (Model): Model object.
            field (DateField): Model's datetime field.

        Returns:
            date: localized datetime.
        """
        original: datetime = getattr(obj, field.name)
        localized: datetime = localtime(original)
        return localized


class DynamicModelFieldDetailView(DetailView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object: Optional[Model] = None

    context_fields_name = "fields"
    unimplemented_types_use_simple_handler = False

    # If fields set to '__all__' it will show fields that their type
    # implemented otherwise will show fields in given tuple/list
    fields: Union[str, tuple, list] = "__all__"
    exclude_fields: Union[tuple, list] = ["id"]
    additional_content: Union[tuple[Callable], list[Callable]] = []

    # Note: each handler handle the type's children too!
    # then their ordering is important. place children types first
    visible_field_types = [
        {
            "types": (BleachField,),
            "handler": FieldValueHandlers.bleach_field_handler,
        },
        {
            "types": (
                CharField,
                TextField,
            ),
            "handler": FieldValueHandlers.simple_field_handler,
        },
        {
            "types": (BooleanField,),
            "handler": FieldValueHandlers.boolean_field_handler,
        },
        {
            "types": (IntegerField,),
            "handler": FieldValueHandlers.integer_field_handler,
        },
        {
            "types": (ImageField,),
            "handler": FieldValueHandlers.image_field_handler,
        },
        {
            "types": (ManyToManyField,),
            "handler": FieldValueHandlers.many_to_many_field_handler,
        },
        {
            "types": (DateTimeField,),
            "handler": FieldValueHandlers.datetime_field_handler,
        },
        {
            "types": (DateField,),
            "handler": FieldValueHandlers.date_field_handler,
        },
    ]

    def _get_visible_types(self) -> tuple[Field]:
        """Returns all types in visible_field_types

        Returns:
            tuple[Field]: Type of visible fields
        """
        v_field_types = tuple()
        for type_handler in self.visible_field_types:
            v_field_types += type_handler.get("types", tuple())

        return v_field_types

    def get_default_fields(self) -> list[str]:
        """Filters visible field names of model and additional_content
            except fields in exclude_fields

        Returns:
            list[str]: Visible field names of model and additional_content
        """

        def _is_visible(field) -> bool:
            """Checks model field's visibility and exclusion

            Args:
                field ([type]): Field to check its visibility

            Returns:
                bool: True if model field's type is visible and didn't excluded
                      else returns False
            """
            return (field.name not in self.exclude_fields) and isinstance(
                field, self._get_visible_types()
            )

        model_fields: list[Field] = self.object._meta.get_fields()
        visible_model_field_names = [
            field.name for field in filter(_is_visible, model_fields)
        ]
        return visible_model_field_names + self.additional_content

    def get_field_value(self, obj: Model, field: Field) -> str:
        """Finds given field in given object and handles its value by its handler

        Args:
            obj (Model): Model object
            field (Field): Field of model to return its value

        Returns:
            str: Field's value in given model object
        """
        for visible_type in self.visible_field_types:
            if isinstance(field, visible_type.get("types", None)):
                return visible_type.get("handler", lambda: None)(obj, field)

        if self.unimplemented_types_use_simple_handler:
            return FieldValueHandlers.simple_field_handler(obj, field)
        else:
            raise ImproperlyConfigured(
                (
                    "Unable to get value of '{}'. '{}' type handler not found."
                    "Hint: You should implement it or set"
                    "unimplemented_types_use_simple_handler = True"
                ).format(field.name, field.__class__.__name__)
            )

    def get_name_values(self) -> list[FieldNameValue]:
        """Gets name and value of fields in self.fields from
            additional_content or from model.

        Returns:
            list[FieldNameValue]: Field names and their value.
        """

        def _get_model_field_name_value(
            obj: Model, field: Field
        ) -> FieldNameValue:
            """Returns field's verbose name and its value.

            Args:
                obj (Model): Model object.
                field (Field): Field of model.

            Returns:
                FieldNameValue: Field's verbose_name and it's value.
            """
            return {
                "name": field.verbose_name,
                "value": self.get_field_value(obj, field),
            }

        def _get_additional_name_value(
            additional_content: Callable,
        ) -> FieldNameValue:
            """Returns additional conetent's name and its value.

            Args:
                additional_content (Callable): Additional content callable
                                               to call and get its value.

            Returns:
                FieldNameValue: short_description and value of
                                additional content.
            """
            callable_name = getattr(
                additional_content,
                "short_description",
                additional_content.__name__,
            )

            return {"name": callable_name, "value": additional_content(self)}

        if self.fields == "__all__":
            # If fields set to '__all__' set fields to default visible fields
            self.fields = self.get_default_fields()

        # If field is in additional_content get field name and value by
        # _get_additional_name_value otherwise try to get get field name
        # and value by _get_model_field_name_value
        return [
            _get_additional_name_value(field)
            if (field in self.additional_content)
            else _get_model_field_name_value(
                self.object, self.object._meta.get_field(field)
            )
            for field in self.fields
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_fields_name] = self.get_name_values()
        return context


class DeleteDeactivationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add submit button
        self.helper = FormHelper()
        self.helper.add_input(
            Submit("create_update", "حذف", css_class="btn-danger")
        )

    DELETE = "delete"
    DEACTIVATE = "deactivate"
    CHOICES = [
        (DEACTIVATE, "غیر فعالسازی"),
        (DELETE, "حذف"),
    ]

    action = forms.ChoiceField(
        choices=CHOICES,
        required=True,
        initial=DEACTIVATE,
        widget=forms.RadioSelect,
        label="عملیات مورد نظر",
    )

    @property
    def action_display(self) -> str:
        """Returns display of chosen action

        Returns:
            str: Display of chosen action
        """
        return dict(self.fields["action"].choices)[self.cleaned_data["action"]]


class DeleteDeactivationView(DeleteView):

    # Delate/Deactivation form
    form = DeleteDeactivationForm
    # Field to choose action by its value
    form_action_field = "action"
    # Delate/Deactivation form context name
    context_action_form_name = "form"

    # Form field and value to set if deactivate chose
    model_deactivation_field = "is_active"
    model_deactivation_value = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def deactivate_object(
        self, obj: Model, deactivation_field: str, deactivation_value: str
    ):
        """Deactivates model object

        Args:
            obj (Model): Model objects
            deactivation_field (str): Field to set deactivation_value
                                      as its value.
            deactivation_value (str): Value to set as deactivated
                                      field's value.
        """
        setattr(obj, deactivation_field, deactivation_value)
        self.object.save()

    def delete_object(self, obj: Model):
        """Deletes model object

        Args:
            obj (Model): model object
        """
        obj.delete()

    def delete_deactivate(self, request: HttpRequest, *args, **kwargs):
        """Deletes/Deactivates model object"""
        self.object = self.get_object()
        success_url = self.get_success_url()
        form = self.form(request.POST)

        if not form.is_valid():
            return HttpResponseBadRequest()

        action = form.cleaned_data[self.form_action_field]

        if action == self.form.DEACTIVATE:
            # Deactivate model object
            self.deactivate_object(
                self.object,
                self.model_deactivation_field,
                self.model_deactivation_value,
            )

        elif action == self.form.DELETE:
            # Delete model object
            self.delete_object(self.object)

        # Message user
        messages.success(
            request,
            f'{form.action_display} "{self.object.title}" با موفقیت انجام شد',
        )

        return redirect(success_url)

    def post(self, request: HttpRequest, *args, **kwargs):
        return self.delete_deactivate(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create instance of form for context and assign it
        context[self.context_action_form_name] = self.form()
        return context
