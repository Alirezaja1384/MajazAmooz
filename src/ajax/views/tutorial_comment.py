import json

from django.http import HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import (DatabaseError, transaction)
from constance import config
from ajax.forms import TutorialCommentForm
from learning.models import (
    TutorialComment, TutorialCommentUpVote,
    TutorialCommentDownVote, TutorialCommentLike
)


class InsertOrDeleteStatus:
    INSERTED = 1
    DELETED = -1
    ERROR = 0


@login_required
def tutorial_comment_create_view(request: HttpRequest):
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

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except Exception as ex:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                         'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})


@login_required
def tutorial_comment_like_view(request: HttpRequest):

    tutorial_comment_like_score = config.TUTORIAL_COMMENT_LIKE_SCORE
    tutorial_comment_like_coin = config.TUTORIAL_COMMENT_LIKE_COIN

    # If request is ajax and tutorial_comment_id sent by client
    if request.method == 'POST' and request.is_ajax():

        before_operation = transaction.savepoint()

        try:

            tutorial_comment_id = int(json.loads(request.body).get('comment_id'))

            # It will throw ObjectDoesNotExist exception
            # if can't find comment
            tutorial_comment = TutorialComment.objects.active_and_confirmed_comments(
                                                       ).select_related('user'
                                                       ).get(id=tutorial_comment_id)

            tutorial_comment_likes = TutorialCommentLike.objects.filter(
                user=request.user, comment=tutorial_comment)

            with transaction.atomic():
                # If tutorial_comment like already exist delete it
                if tutorial_comment_likes.exists():

                    tutorial_comment_like = tutorial_comment_likes.first()
                    # delete tutorial_comment like
                    tutorial_comment_like.delete()

                    return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

                # Else insert tutorial_comment like
                else:

                    TutorialCommentLike.objects.create(user=request.user,
                                                    comment=tutorial_comment,
                                                    score=tutorial_comment_like_score,
                                                    coin=tutorial_comment_like_coin)

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
def tutorial_comment_upvote_view(request: HttpRequest):

    tutorial_comment_upvote_score = config.TUTORIAL_COMMENT_UPVOTE_SCORE
    tutorial_comment_upvote_coin = config.TUTORIAL_COMMENT_UPVOTE_COIN

    # If request is ajax and tutorial_comment_id sent by client
    if request.method == 'POST' and request.is_ajax():

        before_operation = transaction.savepoint()

        try:

            tutorial_comment_id = int(json.loads(request.body).get('comment_id'))

            # It will throw ObjectDoesNotExist exception
            # if can't find comment
            tutorial_comment = TutorialComment.objects.active_and_confirmed_comments(
                                                       ).select_related('user'
                                                       ).get(id=tutorial_comment_id)

            tutorial_comment_upvotes = TutorialCommentUpVote.objects.filter(
                user=request.user, comment=tutorial_comment)

            with transaction.atomic():
                # If tutorial_comment upvote already exist delete it
                if tutorial_comment_upvotes.exists():

                    tutorial_comment_upvote = tutorial_comment_upvotes.first()
                    # delete tutorial_comment upvote
                    tutorial_comment_upvote.delete()

                    return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

                # Else insert tutorial_comment upvote
                else:

                    TutorialCommentUpVote.objects.create(user=request.user,
                                                        comment=tutorial_comment,
                                                        score=tutorial_comment_upvote_score,
                                                        coin=tutorial_comment_upvote_coin)

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
def tutorial_comment_downvote_view(request: HttpRequest):

    tutorial_comment_downvote_score = config.TUTORIAL_COMMENT_DOWNVOTE_SCORE
    tutorial_comment_downvote_coin = config.TUTORIAL_COMMENT_DOWNVOTE_COIN

    # If request is ajax and tutorial_comment_id sent by client
    if request.method == 'POST' and request.is_ajax():

        before_operation = transaction.savepoint()

        try:

            tutorial_comment_id = int(json.loads(request.body).get('comment_id'))

            # It will throw ObjectDoesNotExist exception
            # if can't find comment
            tutorial_comment = TutorialComment.objects.active_and_confirmed_comments(
                                                       ).select_related('user'
                                                       ).get(id=tutorial_comment_id)

            tutorial_comment_downvotes = TutorialCommentDownVote.objects.filter(
                user=request.user, comment=tutorial_comment)

            with transaction.atomic():
                # If tutorial_comment downvote already exist delete it
                if tutorial_comment_downvotes.exists():

                    tutorial_comment_downvote = tutorial_comment_downvotes.first()
                    # delete tutorial_comment downvote
                    tutorial_comment_downvote.delete()

                    return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

                # Else insert tutorial_comment downvote
                else:

                    TutorialCommentDownVote.objects.create(user=request.user,
                                                        comment=tutorial_comment,
                                                        score=tutorial_comment_downvote_score,
                                                        coin=tutorial_comment_downvote_coin)

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
