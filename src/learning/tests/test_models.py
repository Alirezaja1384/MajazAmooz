import random
from copy import deepcopy
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from model_bakery import baker
from shared.models import ConfirmStatusChoices
from learning.models.tutorial_user_relation_models import (
    AbstractTutorialScoreCoinModel,
)
from learning.models import (
    Category,
    Tutorial,
    TutorialComment,
    TutorialLike,
    TutorialUpVote,
    TutorialDownVote,
)


User = get_user_model()


class CategoryTest(TestCase):
    def setUp(self):
        self.category: Category = baker.make_recipe(
            "learning.active_category",
            name="a test category",
            slug="different-slug",
        )

    def test_auto_slug(self):
        """Model baker sets slug automatically but category should generate
        slug automatically even if it set on initialization.
        """
        self.assertEqual(self.category.slug, "a-test-category")

    def test_not_allow_self_parent(self):
        """Category's clean() method should raise validation error
        when category's parent is itself.
        """
        # set parent category to itself
        self.category.parent_category = self.category
        self.assertRaises(ValidationError, self.category.clean)


class TutorialTest(TestCase):
    def setUp(self):
        tutorial: Tutorial = baker.make_recipe("learning.tutorial")
        tutorial.body = "Changed body"
        # confirm_status should not effect because a
        # sensitive data (body) has been changed
        tutorial.confirm_status = ConfirmStatusChoices.CONFIRMED
        tutorial.save()

        self.changed_tutorial = tutorial

    def test_auto_slug(self):
        """Model baker sets slug automatically but category should generate
        slug automatically even if it set on initialization.
        """
        tutorial: Tutorial = baker.make_recipe(
            "learning.tutorial",
            title="A tutorial title",
            slug="different-slug",
        )
        self.assertEqual(tutorial.slug, "a-tutorial-title")

    def test_edit_is_edited(self):
        """Should set 'is_edited=True' if a sensitive data (like body)
        change.
        """
        self.assertTrue(self.changed_tutorial.is_edited)

    def test_edit_last_edit_date(self):
        """Should set 'last_edit_date' if a sensitive data (like body)
        change.
        """
        self.assertIsNotNone(self.changed_tutorial.last_edit_date)

    def test_edit_waiting_for_confirm(self):
        """Should set 'confirm_status' to waiting for confirm
        if a sensitive data (like body) change.
        """
        self.assertEqual(
            self.changed_tutorial.confirm_status,
            ConfirmStatusChoices.WAITING_FOR_CONFIRM,
        )


class TutorialCommentTest(TestCase):
    def setUp(self):
        tutorial: Tutorial = baker.make_recipe("learning.tutorial")

        comment: TutorialComment = baker.make_recipe(
            "learning.tutorial_comment", tutorial=tutorial
        )
        replied_comment: TutorialComment = baker.make_recipe(
            "learning.tutorial_comment", parent_comment=comment
        )

        self.tutorial = tutorial
        self.comment = comment
        self.replied_comment = replied_comment

    def test_not_allow_self_parent(self):
        """Should not allow comment to be parent of itself."""
        self.comment.parent_comment = self.comment
        self.assertRaises(ValidationError, self.comment.clean)

    def test_automatically_set_tutorial_on_replay(self):
        """Should automatically set replied comment's tutorial to
        its parents's tutorial.
        """
        self.assertEqual(self.replied_comment.tutorial, self.comment.tutorial)

    def test_on_edit(self):
        """Should set 'is_edited=True', 'last_edit_date', and
        set 'confirm_status' to 'WAITING_FOR_CONFIRM'.
        """
        edited_comment = deepcopy(self.comment)
        edited_comment.body = "Changed body"
        edited_comment.confirm_status = ConfirmStatusChoices.CONFIRMED
        edited_comment.save()

        self.assertTrue(edited_comment.is_edited)
        self.assertIsNotNone(edited_comment.last_edit_date)
        self.assertEqual(
            edited_comment.confirm_status,
            ConfirmStatusChoices.WAITING_FOR_CONFIRM,
        )


class TutorialUserScoreCoinRelationsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        models = [TutorialLike, TutorialUpVote, TutorialDownVote]
        cls.model = random.choice(models)

        super().setUpClass()

    def setUp(self):
        user: User = baker.make(User)
        author: User = baker.make(User)
        tutorial: Tutorial = baker.make_recipe(
            "learning.tutorial", author=author
        )
        self.user = deepcopy(user)
        self.author = deepcopy(author)
        self.tutorial = deepcopy(tutorial)

        model_instance: AbstractTutorialScoreCoinModel = baker.make(
            self.model,
            user=user,
            tutorial=tutorial,
            score=200,
            coin=250,
        )
        self.model_instance = model_instance

    def test_increase_user_score_coin_on_create(self):
        """Creating model should increase tutorial author's
        coins and scores.
        """
        old_scores = self.author.scores
        old_coins = self.author.coins
        self.author.refresh_from_db()

        self.assertEqual(
            self.author.scores, old_scores + self.model_instance.score
        )
        self.assertEqual(
            self.author.coins, old_coins + self.model_instance.coin
        )

    def test_increase_count_tutorial_model_on_create(self):
        """Creating model should increase its count in tutorial model."""
        old_count = getattr(
            self.tutorial, self.model_instance.tutorial_object_count_field
        )
        self.tutorial.refresh_from_db()
        new_count = getattr(
            self.tutorial, self.model_instance.tutorial_object_count_field
        )

        self.assertEqual(new_count, old_count + 1)

    def test_decrease_user_score_coin_on_delete(self):
        """Deleteing model should decrease tutorial author's
        coins and scores."""
        # Refresh author fields after model creation in setUp()
        self.author.refresh_from_db()
        old_scores = self.author.scores
        old_coins = self.author.coins

        # Delete model
        self.model_instance.delete()
        # Refresh author fields after model delete
        self.author.refresh_from_db()

        self.assertEqual(
            self.author.scores, old_scores - self.model_instance.score
        )
        self.assertEqual(
            self.author.coins, old_coins - self.model_instance.coin
        )

    def test_decrease_count_tutorial_model_on_delete(self):
        """Deleteting model should decrease its count in tutorial model."""

        # Refresh tutorial fields after model creation in setUp()
        self.tutorial.refresh_from_db()
        old_count = getattr(
            self.tutorial, self.model_instance.tutorial_object_count_field
        )

        # Delete model
        self.model_instance.delete()
        # Refresh author fields after model delete
        self.tutorial.refresh_from_db()
        new_count = getattr(
            self.tutorial, self.model_instance.tutorial_object_count_field
        )

        self.assertEqual(new_count, old_count - 1)
