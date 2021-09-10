from unittest import mock
from typing import Optional, Union
from django.test import TestCase
from model_bakery import baker
from learning.models import Tutorial, TutorialTag
from user.forms import TutorialForm


class TutorialFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        tutorial: Tutorial = baker.make_recipe(
            "learning.confirmed_tutorial", is_active=True
        )
        baker.make(TutorialTag, tutorial=tutorial, _quantity=3)

        cls.object = tutorial
        cls.tags = tutorial.tags.all()

    def generate_tags(
        self, tutorial: Optional[Tutorial] = None, count: int = 4
    ) -> list[TutorialTag]:
        """Generates list of TutorialTags.

        Args:
            count (int, optional): Count of tags. Defaults to 4.

        Returns:
            List[TutorialTag]: Generated tags.
        """

        return baker.prepare(
            TutorialTag, tutorial=tutorial or self.object, _quantity=count
        )

    def get_tutorial_dict(
        self,
        tutorial: Optional[Tutorial] = None,
        new_tags: Optional[Union[str, list[TutorialTag]]] = None,
    ) -> dict:
        """Converts tutorial object to a dictionary and replaces
        its tags with given new_tags if provided.

        Args:
            tutorial (Tutorial): Tutorial to get its dict object.
                Defaults to self.object.

            new_tags (Optional[Union[str, list[TutorialTag]]], optional): New
                tags to assign them as tutorial's tags. Defaults to None.

        Returns:
            dict: Dictionary of given tutorial with new tags (if provided).
        """
        if not tutorial:
            tutorial = self.object
        obj_dict: dict = tutorial.__dict__

        if not isinstance(new_tags, str):
            new_tags = ",".join(
                # Convert list of tags (new_tags or original ones) to string
                [str(tag) for tag in (new_tags or tutorial.tags.all())]
            )

        obj_dict["tags"] = new_tags
        return obj_dict

    def assertTagsEquals(
        self,
        first_list: list[TutorialTag],
        second_list: list[TutorialTag],
        *args
    ):
        """Asserts equality of TutorialTags by their title.

        Args:
            first_list (list[TutorialTag]): First list of tags.
            second_list (list[TutorialTag]): Second list of tags.
        """
        self.assertEqual(
            [str(tag) for tag in first_list],
            [str(tag) for tag in second_list],
            *args
        )

    def test_tags_initial_value(self):
        """Should connect tutorial's tag names by `,` as tags'
        initial value.
        """
        form = TutorialForm(instance=self.object)

        self.assertEqual(
            form.fields["tags"].initial,
            ",".join([str(tag) for tag in self.tags]),
        )

    def test_clean_tags_valid_data(self):
        """Should split tags by `,` and turn each of them into
        a TutorialTag object when all tags are valid.
        """
        new_tags = self.generate_tags()
        obj_dict = self.get_tutorial_dict(new_tags=new_tags)

        form = TutorialForm(obj_dict)
        form.is_valid()

        self.assertTagsEquals(form.cleaned_data["tags"], new_tags)

    def test_clean_tags_invalid_data(self):
        """Should not validate when a TutorialTag object is invalid."""
        tag_title_max_length = TutorialTag._meta.get_field("title").max_length
        invalid_tag = "a" * (tag_title_max_length + 1)

        obj_dict = self.get_tutorial_dict(new_tags=invalid_tag)
        form = TutorialForm(obj_dict)

        self.assertFalse(form.is_valid())

    def test_save_tags_create_in_db(self):
        """_save_tags() should save all of the new tags for
        given tutorial.
        """
        new_tags = self.generate_tags()
        obj_dict = self.get_tutorial_dict(new_tags=new_tags)

        form = TutorialForm(obj_dict, instance=self.object)
        form.is_valid()
        form._save_tags()

        self.assertTagsEquals(new_tags, self.object.tags.all())

    def test_save_tags_changed_tag_call_tutorial_on_edit(self):
        """_save_tags() should call tutorial's on_edit when tags
        has changed.
        """
        with mock.patch.object(self.object, "on_edit") as on_edit_mock:
            obj_dict = self.get_tutorial_dict(new_tags=self.generate_tags())
            form = TutorialForm(obj_dict, instance=self.object)
            form.is_valid()
            form._save_tags()

            self.assertTrue(on_edit_mock.called)

    def test_save_tags_unchanged_tag_call_tutorial_on_edit(self):
        """_save_tags() should call tutorial's on_edit when tags
        has changed.
        """
        with mock.patch.object(self.object, "on_edit") as on_edit_mock:
            obj_dict = self.get_tutorial_dict()
            form = TutorialForm(obj_dict, instance=self.object)
            form.is_valid()
            form._save_tags()

            self.assertFalse(on_edit_mock.called)

    @mock.patch.object(TutorialForm, "_save_tags")
    def test_save_tags_commit_false_not_call_save_tags(
        self, _save_tags_mock: mock.MagicMock
    ):
        """Should not call _save_tags when commit=False."""
        obj_dict = self.get_tutorial_dict()
        form = TutorialForm(obj_dict, instance=self.object)
        form.save(commit=False)

        self.assertFalse(_save_tags_mock.called)

    @mock.patch.object(TutorialForm, "_save_tags")
    def test_save_tags_commit_false_assign_save_tags(
        self, _save_tags_mock: mock.MagicMock
    ):
        """Should assign save_tags to _save_tags when commit=False."""
        obj_dict = self.get_tutorial_dict(
            tutorial=baker.prepare_recipe("learning.tutorial")
        )

        form = TutorialForm(obj_dict)
        form.save(commit=False)

        self.assertEqual(form.save_tags, form._save_tags)

    @mock.patch.object(TutorialForm, "_save_tags")
    def test_save_tags_commit_true_call_save_tags(
        self, _save_tags_mock: mock.MagicMock
    ):
        """Should call _save_tags when commit=True."""
        obj_dict = self.get_tutorial_dict(
            tutorial=baker.prepare_recipe("learning.tutorial")
        )

        form = TutorialForm(obj_dict)
        form.save(commit=True)

        self.assertTrue(_save_tags_mock.called)
