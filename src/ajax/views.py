import json

from django.http import HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import (
    DatabaseError, IntegrityError,
    DataError
)
from django.core.exceptions import ObjectDoesNotExist

from learning.models import (
    Tutorial, TutorialLike
)


class InsertOrDeleteStatus:
    INSERTED = 1
    DELETED = -1
    ERROR = 0


@login_required
def insert_or_delete_tutorial_like(request: HttpRequest):

    tutorial_like_score = 5
    tutorial_like_coin = 5

    # If request is ajax and tutorial_id sent by client
    if request.method=='POST' and request.is_ajax():
        try:

            tutorial_id = int(json.loads(request.body).get('tutorial'))
            tutorial = Tutorial.objects.active_and_confirmed_tutorials(
                                        ).prefetch_related('author').get(id=tutorial_id)

            tutorial_author = tutorial.author

            tutorial_likes = TutorialLike.objects.filter(user=request.user, tutorial=tutorial)

            # If tutorial like already exist delete it,
            # decrease tutorial like and
            # decrease author's coins and score
            if tutorial_likes.exists():

                tutorial_like = tutorial_likes.first()

                # decrease tutorial like
                tutorial.likes_count -= 1
                tutorial.save()

                # decrease author's scores and coins
                tutorial_author.scores -= tutorial_like.score
                tutorial_author.coins -= tutorial_like.coin
                tutorial_author.save()

                #delete tutorial like
                tutorial_like.delete()

                return JsonResponse({'status': InsertOrDeleteStatus.DELETED})

            # Else insert tutorial like,
            # increase tutorial like and
            # increase author's coins and score
            else:

                TutorialLike.objects.create(user=request.user, tutorial=tutorial,
                                            score=tutorial_like_score, coin=tutorial_like_coin)
                # increase tutorial like
                tutorial.likes_count += 1
                tutorial.save()

                # increase author's scores and coins
                tutorial_author.scores += tutorial_like_score
                tutorial_author.coins += tutorial_like_coin
                tutorial_author.save()

                return JsonResponse({'status': InsertOrDeleteStatus.INSERTED})

        except (DatabaseError ,IntegrityError, DataError, ObjectDoesNotExist) as ex:
            return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': ex})

    return JsonResponse({'status': InsertOrDeleteStatus.ERROR, 'error': 'درخواست تنها از طریق POST و به صورت Ajax قابل قبول است'})
