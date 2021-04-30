import json

from django.http import HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import (
    DatabaseError, IntegrityError,
    DataError
)
from django.core.exceptions import ObjectDoesNotExist

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
    if request.method=='POST' and request.is_ajax():
        try:

            tutorial_id = int(json.loads(request.body).get('tutorial_id'))
            tutorial = Tutorial.objects.active_and_confirmed_tutorials(
                                        ).prefetch_related('author').get(id=tutorial_id)

            tutorial_author = tutorial.author

            tutorial_likes = TutorialLike.objects.filter(user=request.user, tutorial=tutorial)

            # If tutorial upvote already exist delete it,
            # decrease tutorial upvote and
            # decrease author's coins and score
            if tutorial_likes.exists():

                tutorial_like = tutorial_likes.first()

                # decrease tutorial upvote
                tutorial.likes_count -= 1
                tutorial.save()

                # decrease author's scores and coins
                tutorial_author.scores -= tutorial_like.score
                tutorial_author.coins -= tutorial_like.coin
                tutorial_author.save()

                #delete tutorial upvote
                tutorial_like.delete()

                return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

            # Else insert tutorial upvote,
            # increase tutorial upvote and
            # increase author's coins and score
            else:

                TutorialLike.objects.create(user=request.user, tutorial=tutorial,
                                            score=tutorial_like_score, coin=tutorial_like_coin)
                # increase tutorial upvote
                tutorial.likes_count += 1
                tutorial.save()

                # increase author's scores and coins
                tutorial_author.scores += tutorial_like_score
                tutorial_author.coins += tutorial_like_coin
                tutorial_author.save()

                return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except (DatabaseError ,IntegrityError, DataError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

    return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                         'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})



@login_required
def tutorial_upvote_view(request: HttpRequest):

    tutorial_upvote_score = 2
    tutorial_upvote_coin = 2

    # If request is ajax and tutorial_id sent by client
    if request.method=='POST' and request.is_ajax():
        try:

            tutorial_id = int(json.loads(request.body).get('tutorial_id'))
            tutorial = Tutorial.objects.active_and_confirmed_tutorials(
                                        ).prefetch_related('author').get(id=tutorial_id)

            tutorial_author = tutorial.author

            tutorial_upvotes = TutorialUpVote.objects.filter(user=request.user, tutorial=tutorial)

            # If tutorial upvote already exist delete it,
            # decrease tutorial upvote and
            # decrease author's coins and score
            if tutorial_upvotes.exists():

                tutorial_upvote = tutorial_upvotes.first()

                # decrease tutorial upvote
                tutorial.up_votes_count -= 1
                tutorial.save()

                # decrease author's scores and coins
                tutorial_author.scores -= tutorial_upvote.score
                tutorial_author.coins -= tutorial_upvote.coin
                tutorial_author.save()

                #delete tutorial upvote
                tutorial_upvote.delete()

                return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

            # Else insert tutorial upvote,
            # increase tutorial upvote and
            # increase author's coins and score
            else:

                TutorialUpVote.objects.create(user=request.user, tutorial=tutorial,
                                            score=tutorial_upvote_score, coin=tutorial_upvote_coin)
                # increase tutorial upvote
                tutorial.up_votes_count += 1
                tutorial.save()

                # increase author's scores and coins
                tutorial_author.scores += tutorial_upvote_score
                tutorial_author.coins += tutorial_upvote_coin
                tutorial_author.save()

                return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except (DatabaseError ,IntegrityError, DataError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})

    return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                         'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})

@login_required
def tutorial_downvote_view(request: HttpRequest):

    tutorial_downvote_score = -2
    tutorial_downvote_coin = -2

    # If request is ajax and tutorial_id sent by client
    if request.method=='POST' and request.is_ajax():
        try:

            tutorial_id = int(json.loads(request.body).get('tutorial_id'))
            tutorial = Tutorial.objects.active_and_confirmed_tutorials(
                                        ).prefetch_related('author').get(id=tutorial_id)

            tutorial_author = tutorial.author

            tutorial_downvotes = TutorialDownVote.objects.filter(user=request.user,
                                                                 tutorial=tutorial)

            # If tutorial downvote already exist delete it,
            # decrease tutorial downvote and
            # decrease author's coins and score
            if tutorial_downvotes.exists():

                tutorial_downvote = tutorial_downvotes.first()

                # decrease tutorial downvote
                tutorial.down_votes_count -= 1
                tutorial.save()

                # decrease author's scores and coins
                tutorial_author.scores -= tutorial_downvote.score
                tutorial_author.coins -= tutorial_downvote.coin
                tutorial_author.save()

                #delete tutorial downvote
                tutorial_downvote.delete()

                return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

            # Else insert tutorial downvote,
            # increase tutorial downvote and
            # increase author's coins and score
            else:

                TutorialDownVote.objects.create(user=request.user, tutorial=tutorial,
                                                score=tutorial_downvote_score,
                                                coin=tutorial_downvote_coin)
                # increase tutorial downvote
                tutorial.down_votes_count += 1
                tutorial.save()

                # increase author's scores and coins
                tutorial_author.scores += tutorial_downvote_score
                tutorial_author.coins += tutorial_downvote_coin
                tutorial_author.save()

                return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except TypeError:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'اطلاعات ارسالی صحیح نمی باشد'})

        except (DatabaseError ,IntegrityError, DataError, ObjectDoesNotExist):
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                                 'error': 'خطایی در ثبت اطلاعات رخ داد'})


    return JsonResponse({'status': InsertOrDeleteStatus.ERROR,
                         'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})
