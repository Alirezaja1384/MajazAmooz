" Grade model "
from django.db import models


class Category(models.Model):
    """ Grade model """

    parent_grade = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='child_grades', verbose_name='پایه والد')

    name = models.CharField('نام', max_length=30)

    slug = models.SlugField('اسلاگ', max_length=50, allow_unicode=True)

    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'

    def __str__(self):
        return self.title