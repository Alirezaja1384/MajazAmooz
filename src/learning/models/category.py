""" Category mode """
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django_lifecycle import LifecycleModel, hook, BEFORE_SAVE
from learning.querysets.category_queryset import CategoryQueryset


class Category(LifecycleModel):
    """Category model"""

    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_categories",
        verbose_name="دسته بندی والد",
    )

    name = models.CharField("نام", unique=True, max_length=30)

    slug = models.SlugField(
        "اسلاگ", unique=True, max_length=50, blank=True, allow_unicode=True
    )

    is_active = models.BooleanField("فعال", default=True)

    # Validate data (for admin panel)
    def clean(self):
        if self.id == self.parent_category_id:
            raise ValidationError(
                "والد نمی تواند با دسته بندی فعلی یکسان باشد"
            )

    @hook(BEFORE_SAVE)
    def on_save(self):
        self.slug = slugify(self.name, allow_unicode=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"

    # Custom queryset
    objects = CategoryQueryset.as_manager()
