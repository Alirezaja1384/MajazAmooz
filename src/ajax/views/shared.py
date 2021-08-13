import json
import logging
from typing import Optional, Dict
from django.views.generic import View
from django.db.models import QuerySet
from django.db import transaction, DatabaseError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest


logger = logging.getLogger("database")


class InsertOrDeleteStatus:
    INSERTED = 1
    DELETED = -1
    ERROR = 0


class AjaxView(View):
    """Accepts ajax views and handles them. Calls db_operation()
    method and returns its result as post view's result.

    Raises:
        ImproperlyConfigured: When db_operation didn't implemented.
    """

    data: Optional[Dict] = None
    http_method_names = ["post"]
    db_error_default_text = "خطایی در ثبت اطلاعات رخ داد"

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
                logger.error(ex)

                # Return error result
                return JsonResponse(
                    {
                        "status": InsertOrDeleteStatus.ERROR,
                        "error": self.db_error_default_text,
                    }
                )

        return HttpResponseBadRequest()

    def get_request_data(self):
        """Reads request body and sets its data as self.data"""
        try:
            return json.loads(self.request.body)
        except json.JSONDecodeError:
            return dict()

    def db_operation(self) -> JsonResponse:
        """Handles ajax request's database operations.

        Raises:
            ImproperlyConfigured: It should be implemented by user, otherwise
                will raise ImproperlyConfigured.

        Returns:
            JsonResponse: Result of database operation as JsonResponse.
        """
        raise ImproperlyConfigured("You should configure db_actions first.")

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.data = self.get_request_data()


class AjaxModelCreateDeleteView(LoginRequiredMixin, AjaxView):
    model = None

    def db_operation(self):
        # Set patent objects like tutorial, tutorial_comment
        self.prepare_objects()
        # Create/Delete object
        return self.create_delete_object()

    def prepare_objects(self):
        pass

    def get_objects(self):
        raise ImproperlyConfigured("get_objects should be configured.")

    def create_delete_object(self):
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
