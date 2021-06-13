from typing import TypedDict
import bleach
from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.http import (HttpRequest, HttpResponseBadRequest)
from django.views.generic import (DetailView, DeleteView)
from django.utils.safestring import mark_safe
from django.db.models import (
    Field, Model, CharField, TextField,
    BooleanField, IntegerField, ImageField
)
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django_bleach.models import BleachField
from django_bleach.utils import get_bleach_default_options
from utilities.templatetags.image_utils import image_tag


class FieldNameValue(TypedDict):
    name: str
    value: str


class FieldValueHandlers:

    @staticmethod
    def simple_field_handler(obj: Model, field: Model) -> str:
        """ handles BooleanField and its children

        Args:
            obj (Model): Model object
            field (IntegerField): Models's field

        Returns:
            str: String of field value
        """
        return str(getattr(obj, field.name, ''))

    @staticmethod
    def boolean_field_handler(obj: Model, field: BooleanField) -> str:
        """ handles BooleanField and its children

        Args:
            obj (Model): Model object
            field (IntegerField): Models's field

        Returns:
            str: If field's value is True returns 'بله'
                 else returns 'خیر'
        """
        value = getattr(obj, field.name)
        return 'بله' if value else 'خیر'

    @staticmethod
    def integer_field_handler(obj: Model, field: IntegerField) -> str:
        """ handles IntegerField and its children

        Args:
            obj (Model): Model object
            field (IntegerField): Models's field

        Returns:
            str: If field has choices returns choice display
                 else returns field value
        """
        if field.choices:
            return getattr(obj, f'get_{field.name}_display')()
        else:
            return str(getattr(obj, field.name, ''))

    @staticmethod
    def bleach_field_handler(obj: Model, field: BleachField) -> str:
        """ Handles BleachField

        Args:
            obj (Model): Model object
            field (BleachField): Model's field

        Returns:
            str: Allowed content as safe data
        """
        value = str(getattr(obj, field.name, ''))
        bleach_options = get_bleach_default_options()
        clean_value = bleach.clean(value, **bleach_options)
        return mark_safe(clean_value)

    @staticmethod
    def image_field_handler(obj: Model, field: ImageField) -> str:
        """ Handles ImageField (returns an img tag of the image)

        Args:
            obj (Model): Model object
            field (ImageField): Model's field

        Returns:
            str: An img tag of the image
        """
        image: ImageField = getattr(obj, field.name)
        return image_tag(image=image, alt=str(obj))


class DynamicModelFieldDetailView(DetailView):

    context_fields_name = 'fields'

    exclude_fields = ['id']

    # Note: each handler handle the type's children too!
    # then their ordering is important. place children types first
    visible_field_types = [
        {
            'types': (BleachField,),
            'handler': FieldValueHandlers.bleach_field_handler
        },
        {
            'types': (CharField, TextField,),
            'handler': FieldValueHandlers.simple_field_handler
        },
        {
            'types': (BooleanField,),
            'handler': FieldValueHandlers.boolean_field_handler
        },
        {
            'types': (IntegerField,),
            'handler': FieldValueHandlers.integer_field_handler
        },
        {
            'types': (ImageField,),
            'handler': FieldValueHandlers.image_field_handler
        },
    ]

    def _get_visible_types(self) -> tuple[Field]:
        """ Returns all types in visible_field_types

        Returns:
            tuple[Field]: Type of visible fields
        """
        v_field_types = tuple()
        for type_handler in self.visible_field_types:
            v_field_types += type_handler.get('types', tuple())

        return v_field_types

    def get_visible_fields(self, fields: list[Field]) -> tuple[Field]:
        """ Filters visible fields of given fields except fields in exclude_fields

        Args:
            fields (list[Field]): Fields to check their visibility

        Returns:
            tuple[Field]: Visible fields of given fields
        """
        def _is_visible(field) -> bool:
            """ Checks field's visibility and exclusion

            Args:
                field ([type]): Field to check its visibility

            Returns:
                bool: True if field's type is visible and didn't excluded
                      else returns False
            """
            return (field.name not in self.exclude_fields
                    ) and isinstance(field, self._get_visible_types())

        return tuple(filter(_is_visible, fields))

    def get_field_value(self, obj: Model, field: Field) -> str:
        """ Finds given field in given object and handles its value by its handler

        Args:
            obj (Model): Model object
            field (Field): Field of model to return its value

        Returns:
            str: Field's value in given model object
        """
        for visible_type in self.visible_field_types:
            if isinstance(field, visible_type.get('types', None)):
                return visible_type.get('handler', lambda: None)(obj, field)

    def get_visible_field_name_values(self) -> list[FieldNameValue]:
        """ Visible fields and value of view object

        Returns:
            list[FieldNameValue]: Field names and their value
        """
        def _get_field_name_value_object(obj: Model, field: Field) -> FieldNameValue:
            """ Returns field's verbose name and its value

            Args:
                obj (Model): Model object
                field (Field): Field of model

            Returns:
                FieldNameValue: Field's verbose_name and it's value
            """
            return {'name': field.verbose_name, 'value': self.get_field_value(obj, field)}

        obj = self.get_object()
        visible_fields = self.get_visible_fields(obj._meta.get_fields())
        return [_get_field_name_value_object(obj, v_field) for v_field in visible_fields]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_fields_name] = self.get_visible_field_name_values()

        return context


class DeleteDeactivationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add submit button
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('create_update', 'حذف', css_class='btn-danger'))

    DELETE = 'delete'
    DEACTIVATE = 'deactivate'
    CHOICES = [
        (DEACTIVATE, 'غیر فعالسازی'),
        (DELETE, 'حذف'),
    ]

    action = forms.ChoiceField(
        choices=CHOICES, required=True, initial=DEACTIVATE,
        widget=forms.RadioSelect, label='عملیات مورد نظر')

    @property
    def action_display(self) -> str:
        """ Returns display of chosen action

        Returns:
            str: Display of chosen action
        """
        return dict(self.fields['action'].choices)[self.cleaned_data['action']]


class DeleteDeactivationView(DeleteView):

    # Delate/Deactivation form
    form = DeleteDeactivationForm
    # Field to choose action by its value
    form_action_field = 'action'
    # Delate/Deactivation form context name
    context_action_form_name = 'form'

    # Form field and value to set if deactivate chose
    model_deactivation_field = 'is_active'
    model_deactivation_value = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def deactivate_object(self, obj: Model, deactivation_field: str, deactivation_value: str):
        """ Deactivates model object

        Args:
            obj (Model): Model objects
            deactivation_field (str): Field to set deactivation_value as its value
            deactivation_value (str): Value to set as deactivation_field's value
        """
        setattr(obj, deactivation_field, deactivation_value)
        self.object.save()

    def delete_object(self, obj: Model):
        """ Deletes model object

        Args:
            obj (Model): model object
        """
        obj.delete()

    def delete_deactivate(self, request: HttpRequest, *args, **kwargs):
        """ Deletes/Deactivates model object
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        form = self.form(request.POST)

        if not form.is_valid():
            return HttpResponseBadRequest()

        action = form.cleaned_data[self.form_action_field]

        if action == self.form.DEACTIVATE:
            # Deactivate model object
            self.deactivate_object(self.object, self.model_deactivation_field,
                                   self.model_deactivation_value)

        elif action == self.form.DELETE:
            # Delete model object
            self.delete_object(self.object)

        # Message user
        messages.success(
            request, f'{form.action_display} "{self.object.title}" با موفقیت انجام شد')

        return redirect(success_url)

    def post(self, request: HttpRequest, *args, **kwargs):
        return self.delete_deactivate(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create instance of form for context and assign it
        context[self.context_action_form_name] = self.form()
        return context
