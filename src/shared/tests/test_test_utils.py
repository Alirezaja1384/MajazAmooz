"""Tests for learning.tests.utils"""
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError, models
from . import utils


class ModelTestCaseTest(TestCase):
    """Tests for AbstractModelTestCase"""

    teardown_delete_model = True

    class InvalidModelTestCase(utils.ModelTestCase):
        def test_dummy(self):
            pass

    class ValidModelTestCase(utils.ModelTestCase):
        class TestModel(models.Model):
            name = models.CharField(max_length=10)

            class Meta:
                managed = False

        model = TestModel

        def test_dummy(self):
            pass

    def setUp(self):
        self.invalid_test_case = self.InvalidModelTestCase("test_dummy")
        self.valid_test_case = self.ValidModelTestCase("test_dummy")

        self.valid_test_case.create_model()
        self.model = self.valid_test_case.model

    def test_without_model_raise(self):
        """Should raise ImproperlyConfigured without abstract_model."""
        self.assertRaises(
            ImproperlyConfigured, self.invalid_test_case.setUpClass
        )

    def test_model_database_connection(self):
        """Created model should connect to database properly."""
        try:
            self.model.objects.exists()
        except DatabaseError:
            self.fail("Database connection failed. Model is broken!")

    def test_delete_model_connect_db_error(self):
        """After calling delete_model(), model should not
        be able to connect to the Database.
        """
        # Delete model's table
        self.valid_test_case.delete_model()
        # Prevent from re-deleting model
        self.teardown_delete_model = False

        self.assertRaises(DatabaseError, self.model.objects.exists)

    def tearDown(self):
        if self.teardown_delete_model:
            self.valid_test_case.delete_model()
