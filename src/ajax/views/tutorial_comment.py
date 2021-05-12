import json

from django.http import HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError

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

    tutorial_comment_like_score = 3
    tutorial_comment_like_coin = 3

    # If request is ajax and tutorial_comment_id sent by client
    if request.method == 'POST' and request.is_ajax():
        try:

            tutorial_comment_id = int(json.loads(request.body).get('comment_id'))
            tutorial_comment = TutorialComment.objects.active_and_confirmed_comments(
                                                       ).prefetch_related('user'
                                                       ).get(id=tutorial_comment_id)

            tutorial_comment_user = tutorial_comment.user

            tutorial_comment_likes = TutorialCommentLike.objects.filter(
                user=request.user, comment=tutorial_comment)

            # If tutorial_comment like already exist delete it,
            # decrease tutorial_comment like and
            # decrease user's coins and score
            if tutorial_comment_likes.exists():

                tutorial_comment_like = tutorial_comment_likes.first()

                # decrease tutorial_comment like
                tutorial_comment.likes_count -= 1
                tutorial_comment.save()

                # decrease user's scores and coins
                tutorial_comment_user.scores -= tutorial_comment_like.score
                tutorial_comment_user.coins -= tutorial_comment_like.coin
                tutorial_comment_user.save()

                # delete tutorial_comment like
                tutorial_comment_like.delete()

                return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

            # Else insert tutorial_comment like,
            # increase tutorial_comment like and
            # increase user's coins and score
            else:

                TutorialCommentLike.objects.create(user=request.user,
                                                       comment=tutorial_comment,
                                                       score=tutorial_comment_like_score,
                                                       coin=tutorial_comment_like_coin)

                # increase tutorial_comment like
                tutorial_comment.likes_count += 1
                tutorial_comment.save()

                # increase user's scores and coins
                tutorial_comment_user.scores += tutorial_comment_like_score
                tutorial_comment_user.coins += tutorial_comment_like_coin
                tutorial_comment_user.save()

                return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except Exception as ex:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    else:
        return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                             'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})


@login_required
def tutorial_comment_upvote_view(request: HttpRequest):

    tutorial_comment_upvote_score = 0
    tutorial_comment_upvote_coin = 0

    # If request is ajax and tutorial_comment_id sent by client
    if request.method == 'POST' and request.is_ajax():
        try:

            tutorial_comment_id = int(json.loads(request.body).get('comment_id'))
            tutorial_comment = TutorialComment.objects.active_and_confirmed_comments(
                                                       ).prefetch_related('user'
                                                       ).get(id=tutorial_comment_id)

            tutorial_comment_user = tutorial_comment.user

            tutorial_comment_upvotes = TutorialCommentUpVote.objects.filter(
                user=request.user, comment=tutorial_comment)

            # If tutorial_comment upvote already exist delete it,
            # decrease tutorial_comment upvote and
            # decrease user's coins and score
            if tutorial_comment_upvotes.exists():

                tutorial_comment_upvote = tutorial_comment_upvotes.first()

                # decrease tutorial_comment upvote
                tutorial_comment.up_votes_count -= 1
                tutorial_comment.save()

                # decrease user's scores and coins
                tutorial_comment_user.scores -= tutorial_comment_upvote.score
                tutorial_comment_user.coins -= tutorial_comment_upvote.coin
                tutorial_comment_user.save()

                # delete tutorial_comment upvote
                tutorial_comment_upvote.delete()

                return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

            # Else insert tutorial_comment upvote,
            # increase tutorial_comment upvote and
            # increase user's coins and score
            else:

                TutorialCommentUpVote.objects.create(user=request.user,
                                                     comment=tutorial_comment,
                                                     score=tutorial_comment_upvote_score,
                                                     coin=tutorial_comment_upvote_coin)

                # increase tutorial_comment upvote
                tutorial_comment.up_votes_count += 1
                tutorial_comment.save()

                # increase user's scores and coins
                tutorial_comment_user.scores += tutorial_comment_upvote_score
                tutorial_comment_user.coins += tutorial_comment_upvote_coin
                tutorial_comment_user.save()

                return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except Exception as ex:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    else:
        return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                             'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})


@login_required
def tutorial_comment_downvote_view(request: HttpRequest):

    tutorial_comment_downvote_score = 0
    tutorial_comment_downvote_coin = 0

    # If request is ajax and tutorial_comment_id sent by client
    if request.method == 'POST' and request.is_ajax():
        try:

            tutorial_comment_id = int(json.loads(request.body).get('comment_id'))
            tutorial_comment = TutorialComment.objects.active_and_confirmed_comments(
                                                       ).prefetch_related('user'
                                                       ).get(id=tutorial_comment_id)

            tutorial_comment_user = tutorial_comment.user

            tutorial_comment_downvotes = TutorialCommentDownVote.objects.filter(
                user=request.user, comment=tutorial_comment)

            # If tutorial_comment downvote already exist delete it,
            # decrease tutorial_comment downvote and
            # decrease user's coins and score
            if tutorial_comment_downvotes.exists():

                tutorial_comment_downvote = tutorial_comment_downvotes.first()

                # decrease tutorial_comment downvote
                tutorial_comment.down_votes_count -= 1
                tutorial_comment.save()

                # decrease user's scores and coins
                tutorial_comment_user.scores -= tutorial_comment_downvote.score
                tutorial_comment_user.coins -= tutorial_comment_downvote.coin
                tutorial_comment_user.save()

                # delete tutorial_comment downvote
                tutorial_comment_downvote.delete()

                return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

            # Else insert tutorial_comment downvote,
            # increase tutorial_comment downvote and
            # increase user's coins and score
            else:

                TutorialCommentDownVote.objects.create(user=request.user,
                                                       comment=tutorial_comment,
                                                       score=tutorial_comment_downvote_score,
                                                       coin=tutorial_comment_downvote_coin)

                # increase tutorial_comment downvote
                tutorial_comment.down_votes_count += 1
                tutorial_comment.save()

                # increase user's scores and coins
                tutorial_comment_user.scores += tutorial_comment_downvote_score
                tutorial_comment_user.coins += tutorial_comment_downvote_coin
                tutorial_comment_user.save()

                return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except Exception as ex:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex.args})

    else:
        return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                             'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})
