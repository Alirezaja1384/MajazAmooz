from django.views.generic import ListView
from django.http import QueryDict
from constance import config
from learning.models import Tutorial, Category
from learning.filters import TutorialArchiveFilterSet


class TutorialListView(ListView):
    model = Tutorial
    template_name = "learning/tutorials_archive.html"

    page_kwarg = "page"
    context_object_name = "tutorials"

    def get_paginate_by(self, queryset):
        return config.LEARNING_TUTORIAL_ARCHIVE_PAGINATE_BY

    def get_queryset(self):
        # All confirmed and active tutorials
        tutorials = (
            Tutorial.objects.order_by("-create_date")
            .only_main_fields()
            .active_and_confirmed_tutorials()
        )

        # create_date=order_by and update it with request.GET
        # (order_by=create_date if request.GET doesn't contain order_by)
        filters = QueryDict("order_by=create_date", mutable=True)
        filters.update(self.request.GET)

        # Filter and order tutorials, then annonate comments_count
        tutorials = TutorialArchiveFilterSet(
            filters, tutorials
        ).qs.annonate_comments_count()

        return tutorials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = self.request.GET.get("category")
        if category_slug:
            context["category"] = (
                Category.objects.active_categories()
                .filter(slug=category_slug)
                .first()
            )

        return context
