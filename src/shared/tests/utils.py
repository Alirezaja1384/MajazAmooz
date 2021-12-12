import logging
from typing import Type
from django.test import TestCase
from django.db import connection
from django.db.models import Model
from django.db.utils import ProgrammingError
from django.core.exceptions import ImproperlyConfigured


class ModelTestCase(TestCase):
    """A testcase that creates model wen it's unmanaged (Can be done
    by setting `managed = False` in Meta class).

    Raises:
        ImproperlyConfigured: When model didn't specified or it'd None.
    """

    model: Type[Model]

    @classmethod
    def setUpClass(cls):
        if not getattr(cls, "model", None):
            raise ImproperlyConfigured(
                "model should be configured to use ModelTestCase."
            )

        # Try to delete model if it exists.
        # Note: there is no need to delete model in tearDownClass because
        #       It will be deleted automatically in next SetUpClass.
        cls.delete_model()
        # Create the dummy model.
        cls.create_model()

        super().setUpClass()

    @classmethod
    def create_model(cls):
        """Creates model schema in database."""
        # Create the test model's table
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(cls.model)

    @classmethod
    def delete_model(cls):
        """Deletes class's model from database."""
        # Delete model's table
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(cls.model)
        except ProgrammingError:
            pass


def prevent_request_warnings(original_function):
    """
    If we need to test for 404s or 405s this decorator can prevent the
    request class from throwing warnings.
    """

    def new_function(*args, **kwargs):
        # raise logging level to ERROR
        logger = logging.getLogger("django.request")
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        # trigger original function that would throw warning
        original_function(*args, **kwargs)

        # lower logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function
