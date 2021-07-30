from django.db import models
from django.contrib.auth import get_user_model
from model_bakery import baker
from shared.tests.utils import ModelTestCase
from learning.models import Tutorial
from learning.models.tutorial_user_relation_models import (
    AbstractTutorialScoreCoinModel,
)
from ajax.views import tutorial_views
from .utils import ajax_request

User = get_user_model()


class TutorialUserRelationCreateDeleteViewTest(ModelTestCase):
    class TestTutorialUserScoreCoinModel(AbstractTutorialScoreCoinModel):
        user = models.ForeignKey(User, models.CASCADE)
        tutorial = models.ForeignKey(Tutorial, models.CASCADE)

        class Meta:
            managed = False

    model = TestTutorialUserScoreCoinModel

    @classmethod
    def setUpTestData(cls):
        cls.tutorial = baker.make_recipe(
            "learning.confirmed_tutorial", is_active=True
        )
        cls.user = baker.make(User)

    def setUp(self):
        self.view = tutorial_views.BaseView.as_view(model=self.model)
        self.request = ajax_request(
            data={"tutorial_id": self.tutorial.pk}, user=self.user
        )

    def test_view_create_model_object(self):
        """Should create model object when it doesn't exist."""
        self.view(self.request)
        self.assertTrue(
            self.model.objects.filter(
                user=self.user, tutorial=self.tutorial
            ).exists()
        )

    def test_view_delete_model_object(self):
        """Should delete model object when it exists."""
        model_obj = self.model.objects.create(
            user=self.user, tutorial=self.tutorial
        )
        self.view(self.request)

        self.assertNotIn(model_obj, self.model.objects.all())
