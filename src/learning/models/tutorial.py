""" Tutorial model """
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django_resized import ResizedImageField
from django_lifecycle import LifecycleModel, hook, BEFORE_UPDATE, BEFORE_SAVE
from shared.models import BleachField
from shared.models import ConfirmStatusChoices
from learning.querysets.tutorial_queryset import TutorialQueryset


class Tutorial(LifecycleModel):
    """Tutorial model"""

    title = models.CharField(max_length=30, unique=True, verbose_name="عنوان")

    slug = models.SlugField(
        max_length=50,
        allow_unicode=True,
        unique=True,
        blank=True,
        verbose_name="اسلاگ",
    )

    short_description = BleachField(max_length=250, verbose_name="توضیح کوتاه")

    body = BleachField(verbose_name="بدنه")

    user_views_count = models.PositiveIntegerField(
        verbose_name="بازدید کاربران", default=0
    )

    up_votes_count = models.PositiveIntegerField(
        verbose_name="امتیاز مثبت", default=0
    )
    down_votes_count = models.PositiveIntegerField(
        verbose_name="امتیاز منفی", default=0
    )

    likes_count = models.PositiveIntegerField(
        verbose_name="لایک ها", default=0
    )

    image = ResizedImageField(
        upload_to="images/tutorial_thumbnails",
        default="default/learning/tutorial-image.png",
        size=[960, 540],
        crop=["middle", "center"],
        verbose_name="تصویر",
    )

    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name="زمان انتشار"
    )

    last_edit_date = models.DateTimeField(
        blank=True, null=True, verbose_name="زمان آخرین ویرایش"
    )

    confirm_status = models.IntegerField(
        choices=ConfirmStatusChoices.choices,
        null=False,
        blank=False,
        default=ConfirmStatusChoices.WAITING_FOR_CONFIRM,
        verbose_name="وضعیت تایید",
    )

    is_edited = models.BooleanField(default=False, verbose_name="ویرایش شده")

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # Relations
    author = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="tutorials",
        verbose_name="نویسنده",
    )

    categories = models.ManyToManyField(
        to="learning.Category",
        related_name="tutorials",
        blank=True,
        verbose_name="دسته بندی ها",
    )

    viewers = models.ManyToManyField(
        "authentication.User",
        through="TutorialView",
        related_name="viewed_tutorials",
        verbose_name="بازدید ها",
    )

    likers = models.ManyToManyField(
        "authentication.User",
        through="TutorialLike",
        related_name="liked_tutorials",
        verbose_name="لایک ها",
    )

    up_voters = models.ManyToManyField(
        "authentication.User",
        through="TutorialUpVote",
        related_name="up_voted_tutorials",
        verbose_name="امتیاز های مثبت",
    )

    down_voters = models.ManyToManyField(
        "authentication.User",
        through="TutorialDownVote",
        related_name="down_voted_tutorials",
        verbose_name="امتیاز های منفی",
    )

    # Custom manager
    objects = TutorialQueryset.as_manager()

    @hook(
        BEFORE_UPDATE,
        when_any=["title", "slug", "short_description", "body", "image"],
        has_changed=True,
    )
    def on_edit(self):
        self.is_edited = True
        self.last_edit_date = timezone.now()
        self.confirm_status = ConfirmStatusChoices.WAITING_FOR_CONFIRM

    @hook(BEFORE_SAVE)
    def on_save(self):
        self.slug = slugify(self.title, allow_unicode=True)

    class Meta:
        verbose_name = "آموزش"
        verbose_name_plural = "آموزش ها"
        ordering = ("-create_date",)
        permissions = (("confirm_disprove_tutorial", "تایید/رد آموزش ها"),)

    def __str__(self):
        return self.title

    def get_related_tutorials(
        self, tutorial_count: int = 5
    ) -> TutorialQueryset:
        """Related tutorials to this tutorial (by joint categories).

        Args:
            tutorial_count (int, optional): Expected count of tutorial.
                Defaults to 5.

        Returns:
            TutorialQueryset: Related tutorials to this one.
        """

        def _flat_categories_parents(categories: list):
            """Returns list of categories and their parents"""
            result = categories

            for category in categories:
                while category.parent_category:
                    category = category.parent_category
                    result.append(category)

            # Distinct result
            return list(dict.fromkeys(result))

        categories_and_parents = list(self.categories.all())
        # If tutorial doesn't have any active category return empty
        if len(categories_and_parents) == 0:
            return Tutorial.objects.none()

        categories = _flat_categories_parents(categories_and_parents)

        # Get tutorials with joint categories
        # Note: use self.__class__.objects because
        # objects is not accessible by model instance
        related_tutorials = self.__class__.objects.exclude(
            pk=self.pk
        ).filter_by_categories(categories, tutorial_count)

        return related_tutorials


class TutorialTag(models.Model):
    """TutorialTag model"""

    title = models.CharField(max_length=20, verbose_name="عنوان")

    tutorial = models.ForeignKey(
        Tutorial,
        on_delete=models.CASCADE,
        related_name="tags",
        verbose_name="آموزش",
    )

    class Meta:
        verbose_name = "کلیدواژه"
        verbose_name_plural = "کلیدواژه ها"

    def __str__(self):
        return self.title
