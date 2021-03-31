""" Tutorial view """
from django.views.generic import DetailView

from ..models import Tutorial


# TODO: implement recommended_tutorials, liked_by_current_user
class TutorialDetailView(DetailView):
    """ Tutorial view """
    template_name = 'learning/tutorial.html'

    context_object_name = 'tutorial'

    def get_queryset(self):

        queryset = Tutorial.objects.filter(
            is_active=True, confirm_status=1).select_related('author')

        return queryset
