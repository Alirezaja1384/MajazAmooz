from django.views.generic import ListView
from django.db.models import (Count, Q)
from django.http import QueryDict
from constance import config
from learning.models import (Tutorial, Category)
from learning.filters import TutorialArchiveFilterSet
from utilities.models import ConfirmStatusChoices


class TutorialListView(ListView):
    model = Tutorial
    template_name = "learning/tutorials_archive.html"

    page_kwarg = 'page'
    context_object_name = 'tutorials'

    def get_paginate_by(self, queryset):
        return config.LEARNING_TUTORIAL_ARCHIVE_PAGINATE_BY

    def get_queryset(self):
        # All confirmed and active tutorials
        tutorials = Tutorial.objects.order_by('-create_date').only(
            'title', 'slug', 'short_description', 'likes_count', 'image'
        ).active_and_confirmed_tutorials()

        # create_date=order_by and update it with request.GET
        # (order_by=create_date if request.GET doesn't contain order_by)
        filters = QueryDict('order_by=create_date', mutable=True)
        filters.update(self.request.GET)

        # Filter and order tutorials
        tutorials = TutorialArchiveFilterSet(filters, tutorials).qs

        # Annonate comments_count
        # Note: if distinct=False it will count comments
        #       multiple times then count will go wrong
        tutorials = tutorials.annotate(
            comments_count=Count('comments', distinct=True, filter=Q(comments__is_active=True) &
                                 Q(comments__confirm_status=ConfirmStatusChoices.CONFIRMED)))

        return tutorials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = self.request.GET.get('category')
        if category_slug:
            context['category'] = Category.objects.filter(slug=category_slug,
                                                          is_active=True).first()

        return context
