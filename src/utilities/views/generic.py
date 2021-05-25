from typing import TypedDict
from django.views.generic import DetailView
from django.db.models import (
    Field, Model,
    CharField, TextField,
    BooleanField, IntegerField
)


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


class DynamicModelFieldDetailView(DetailView):

    context_fields_name = 'fields'

    exclude_fields = ['id']
    visible_field_types = [
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
