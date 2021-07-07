import logging
from typing import Optional
from django.views.generic import View
from django.db.models import QuerySet
from django.db import transaction, DatabaseError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest


class InsertOrDeleteStatus:
    INSERTED = 1
    DELETED = -1
    ERROR = 0


class AjaxView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        if request.is_ajax():
            try:
                # Create a db savepoint
                before_operation = transaction.savepoint()
                # Create/Delete object
                return self.db_operation()

            except TypeError:
                return HttpResponseBadRequest()

            except DatabaseError as ex:
                # Rollback db operation
                transaction.rollback(before_operation)

                # Log error
                logger = logging.getLogger("database")
                logger.error(ex)

                # Return error result
                return JsonResponse(
                    {
                        "status": InsertOrDeleteStatus.ERROR,
                        "error": "خطایی رخ داد",
                    }
                )

        return HttpResponseBadRequest()

    def db_operation(self):
        raise ImproperlyConfigured("You should configure db_actions first.")


class AjaxScoreCoinCreateDeleteView(LoginRequiredMixin, AjaxView):
    model = None
    http_method_names = ["post"]

    score: Optional[int] = None
    coin: Optional[int] = None

    def db_operation(self):
        # Set patent objects like tutorial, tutorial_comment
        self.set_parent_objects()
        # Create/Delete object
        return self.create_delete_object()

    def set_parent_objects(self):
        pass

    def get_objects(self):
        raise ImproperlyConfigured("get_objects should be configured.")

    def create_delete_object(self):
        if (self.model is None) or (self.score is None) or (self.coin is None):
            raise ImproperlyConfigured(
                "You should configure model type, score and coin."
            )

        objs = self.get_objects()
        # If tutorial upvote already exist delete it
        if objs.exists():
            # delete object
            self.delete_object(objs)
            return JsonResponse({"status": InsertOrDeleteStatus.DELETED})
        # Else insert tutorial upvote
        else:
            self.create_object()
            return JsonResponse({"status": InsertOrDeleteStatus.INSERTED})

    def delete_object(self, objs: QuerySet):
        obj = objs.first()
        # Call object's delete to ensure does
        # before_delete operations
        obj.delete()

    def create_object(self):
        raise ImproperlyConfigured(
            "You should configure create_object to use it."
        )
