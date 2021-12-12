from typing import Optional
from django.db import models
from django.test import TestCase
from django.utils import timezone
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from model_bakery import baker
from shared.models import ConfirmStatusChoices
from shared.tests.utils import ModelTestCase
from learning.models import TutorialComment
from learning.models.tutorial_comment_user_relation_models import (
    AbstractScoreCoinModel,
)
from ajax.views import tutorial_comment_views
from ajax.views.shared import InsertOrDeleteStatus
from .utils import ajax_request

User = get_user_model()


class TutorialCommentUserRelationCreateDeleteViewTest(ModelTestCase):
    class TestTutorialCommentUserScoreCoinModel(AbstractScoreCoinModel):
        user = models.ForeignKey(User, models.DO_NOTHING)
        comment = models.ForeignKey(TutorialComment, models.DO_NOTHING)

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


class TutorialCommentCreateViewTest(TestCase):
    model = TutorialComment

    @classmethod
    def setUpTestData(cls):
        comment: TutorialComment = baker.prepare_recipe(
            "learning.tutorial_comment"
        )
        cls.user = baker.make(User)
        cls.comment = comment

    def setUp(self):
        self.view = tutorial_comment_views.TutorialCommentCreateView.as_view()

    def make_request(
        self, comment: Optional[TutorialComment] = None, **additional_data
    ) -> HttpRequest:
        """Makes a http ajax request with given comment and additional data.

        Args:
            comment (Optional[TutorialComment], optional): TutorialComment
                object to make request by its fields. Default to None. Uses
                `self.comment` if comment not provided.

            **additional_data: Any additional keyword argument will be
                used as request data.

        Returns:
            HttpRequest: Created request.
        """
        if not comment:
            comment = self.comment

        data = {
            "title": comment.title,
            "body": comment.body,
            "allow_reply": comment.allow_reply,
            "notify_replies": comment.notify_replies,
            "tutorial": comment.tutorial_id,
            "parent_comment": comment.parent_comment_id,
            **additional_data,
        }

        return ajax_request(data=data, user=self.user)

    def test_create_comment(self):
        """Should create model object in database."""
        self.view(self.make_request())
        self.assertTrue(
            self.model.objects.filter(title=self.comment.title).exists()
        )

    def test_auto_specify_user(self):
        """Should automatically use logged-in user as comment's user."""
        request = self.make_request()
        self.view(request)

        comment: TutorialComment = self.model.objects.get(
            title=self.comment.title
        )

        self.assertEqual(comment.user, request.user)

    def test_response_inserted_status(self):
        """Should return a JsonResponse with INSERTED status."""
        response = self.view(self.make_request())
        self.assertJSONEqual(
            response.content, {"status": InsertOrDeleteStatus.INSERTED}
        )

    def test_ignore_sensitive_data(self):
        """Should ignore any sensitive data from request."""
        sensitive_field_values = {
            "is_edited": True,
            "likes_count": 5,
            "up_votes_count": 10,
            "down_votes_count": 8,
            "user_id": baker.make(User).pk,
            "confirm_status": ConfirmStatusChoices.CONFIRMED,
            # 2 days ago
            "create_date": timezone.now() - timezone.timedelta(days=2),
            # Yesterday
            "last_edit_date": timezone.now() - timezone.timedelta(days=1),
        }
        request = self.make_request(self.comment, **sensitive_field_values)
        self.view(request)

        comment: TutorialComment = self.model.objects.get(
            title=self.comment.title
        )

        # None of sensitive fields' value should be equal to sent value
        for field_val in sensitive_field_values.items():
            self.assertNotEqual(getattr(comment, field_val[0]), field_val[1])
