import json

from django.http import HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import (
    DatabaseError, IntegrityError,
    DataError
)
from django.core.exceptions import ObjectDoesNotExist

from ajax.forms import TutorialCommentForm


class InsertOrDeleteStatus:
    INSERTED = 1
    DELETED = -1
    ERROR = 0


@login_required
def tutorial_comment_create(request: HttpRequest):
    # If request is ajax and tutorial_id sent by client
    if request.method == 'POST' and request.is_ajax():
        try:
            tutorial_comment = json.loads(request.body)
            tutorial_comment["user"] = request.user

            form = TutorialCommentForm(tutorial_comment)

            if form.is_valid():
                form.save()
            else:
                return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                     'error': form.errors})

            return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except (DatabaseError, IntegrityError, DataError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except Exception as ex:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                         'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})
