from django.db import models
from django.contrib.auth import get_user_model
from model_bakery import baker
from shared.tests.utils import ModelTestCase
from learning.models import TutorialComment
from learning.models.tutorial_comment_user_relation_models import (
    AbstractCommentScoreCoinModel,
)
from ajax.views import tutorial_comment_views
from .utils import ajax_request

User = get_user_model()


class TutorialCommentUserRelationCreateDeleteViewTest(ModelTestCase):
    class TestTutorialCommentUserScoreCoinModel(AbstractCommentScoreCoinModel):
        user = models.ForeignKey(User, models.CASCADE)
        comment = models.ForeignKey(TutorialComment, models.CASCADE)

        class Meta:
            managed = False

    model = TestTutorialCommentUserScoreCoinModel

    @classmethod
    def setUpTestData(cls):
        cls.comment = baker.make_recipe(
            "learning.confirmed_tutorial_comment", is_active=True
        )
        cls.user = baker.make(User)

    def setUp(self):
        self.view = tutorial_comment_views.BaseView.as_view(model=self.model)
        self.request = ajax_request(
            data={"comment_id": self.comment.pk}, user=self.user
        )

    def test_view_create_model_object(self):
        """Should create model object when it doesn't exist."""
        self.view(self.request)
        self.assertTrue(
            self.model.objects.filter(
                user=self.user, comment=self.comment
            ).exists()
        )

    def test_view_delete_model_object(self):
        """Should delete model object when it exists."""
        model_obj = self.model.objects.create(
            user=self.user, comment=self.comment
        )
        self.view(self.request)

        self.assertNotIn(model_obj, self.model.objects.all())
