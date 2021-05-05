from django.views.generic import ListView
from django.db.models import (Count, Q)

from learning.models import Tutorial
from utilities.model_utils import ConfirmStatusChoices


# TODO: Add category to context
# TODO: Apply filters
# TODO: Apply orderings
# TODO: Template paginator
class TutorialListView(ListView):
    model = Tutorial
    template_name = "learning/tutorials_archive.html"

    paginate_by = 15
    page_kwarg = 'page'
    context_object_name = 'tutorials'


    def get_queryset(self):
        tutorials = Tutorial.objects.active_and_confirmed_tutorials().order_by('-create_date').only(
            'title', 'slug', 'short_description', 'likes_count', 'image').annotate(
            comments_count=Count('comments', filter=Q(
                comments__confirm_status=ConfirmStatusChoices.CONFIRMED)))

        return tutorials
