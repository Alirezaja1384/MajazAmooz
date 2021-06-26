from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from learning.models import Tutorial
from shared.templatetags.image_utils import image_url


class ImageUtilsTest(TestCase):
    def setUp(self):
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        uploaded = SimpleUploadedFile(
            "test.gif", small_gif, content_type="image/gif"
        )

        self.tutorial_with_image = Tutorial.objects.create(
            title="Title 1",
            short_description="Short description 1",
            body="Body 1",
            image=uploaded,
        )

        self.tutorial_without_image = Tutorial.objects.create(
            title="Title 2",
            short_description="Short description 2",
            body="Body 2",
            image=None,
        )

    def test_return_image_url(self):
        url: str = image_url(self.tutorial_with_image.image)
        self.assertEqual(url, self.tutorial_with_image.image.url)

    def test_return_not_found(self):
        url: str = image_url(self.tutorial_without_image.image)
        self.assertTrue(url.endswith("not-found.png"))
