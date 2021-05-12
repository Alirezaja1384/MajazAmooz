import json

from django.http import HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import (DatabaseError, transaction)
from learning.models import (
    Tutorial, TutorialLike,
    TutorialUpVote, TutorialDownVote
)


class InsertOrDeleteStatus:
    INSERTED = 1
    DELETED = -1
    ERROR = 0


@login_required
def tutorial_like_view(request: HttpRequest):

    tutorial_like_score = 5
    tutorial_like_coin = 5

    # If request is ajax and tutorial_id sent by client
    if request.method == 'POST' and request.is_ajax():

        before_operation = transaction.savepoint()

        try:

            tutorial_id = int(json.loads(request.body).get('tutorial_id'))

            # It will throw ObjectDoesNotExist exception
            # if can't find tutorial
            tutorial = Tutorial.objects.active_and_confirmed_tutorials(
            ).select_related('author').get(id=tutorial_id)

            tutorial_likes = TutorialLike.objects.filter(
                user=request.user, tutorial=tutorial)

            with transaction.atomic():
                # If tutorial upvote already exist delete it
                if tutorial_likes.exists():

                    tutorial_like = tutorial_likes.first()
                    # delete tutorial upvote
                    tutorial_like.delete()

                    return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

                # Else insert tutorial upvote
                else:
                    TutorialLike.objects.create(user=request.user, tutorial=tutorial,
                                                score=tutorial_like_score, coin=tutorial_like_coin)

                    return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except Exception as ex:
            transaction.rollback(before_operation)
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    else:
        return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                             'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})


@login_required
def tutorial_upvote_view(request: HttpRequest):

    tutorial_upvote_score = 0
    tutorial_upvote_coin = 0

    # If request is ajax and tutorial_id sent by client
    if request.method == 'POST' and request.is_ajax():

        before_operation = transaction.savepoint()

        try:

            tutorial_id = int(json.loads(request.body).get('tutorial_id'))

            # It will throw ObjectDoesNotExist exception
            # if can't find tutorial
            tutorial = Tutorial.objects.active_and_confirmed_tutorials(
            ).select_related('author').get(id=tutorial_id)

            tutorial_upvotes = TutorialUpVote.objects.filter(
                user=request.user, tutorial=tutorial)

            with transaction.atomic():
                # If tutorial upvote already exist delete it
                if tutorial_upvotes.exists():
                    tutorial_upvote = tutorial_upvotes.first()
                    # delete tutorial upvote
                    tutorial_upvote.delete()

                    return JsonResponse({'status': InsertOrDeleteStatus.DELETED})
                # Else insert tutorial upvote
                else:
                    TutorialUpVote.objects.create(user=request.user, tutorial=tutorial,
                                                score=tutorial_upvote_score,
                                                coin=tutorial_upvote_coin)

                    return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except Exception as ex:
            transaction.rollback(before_operation)
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    else:
        return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                             'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})


@login_required
def tutorial_downvote_view(request: HttpRequest):

    tutorial_downvote_score = 0
    tutorial_downvote_coin = 0

    # If request is ajax and tutorial_id sent by client
    if request.method == 'POST' and request.is_ajax():

        before_operation = transaction.savepoint()

        try:

            tutorial_id = int(json.loads(request.body).get('tutorial_id'))

            # It will throw ObjectDoesNotExist exception
            # if can't find tutorial
            tutorial = Tutorial.objects.active_and_confirmed_tutorials(
            ).select_related('author').get(id=tutorial_id)

            tutorial_downvotes = TutorialDownVote.objects.filter(user=request.user,
                                                                 tutorial=tutorial)
            with transaction.atomic():
                # If tutorial downvote already exist delete it
                if tutorial_downvotes.exists():

                    tutorial_downvote = tutorial_downvotes.first()
                    # delete tutorial downvote
                    tutorial_downvote.delete()

                    return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

                # Else insert tutorial downvote
                else:
                    TutorialDownVote.objects.create(user=request.user, tutorial=tutorial,
                                                    score=tutorial_downvote_score,
                                                    coin=tutorial_downvote_coin)

                    return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except Exception as ex:
            transaction.rollback(before_operation)
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    else:
        return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                             'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})
