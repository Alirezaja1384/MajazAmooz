from django.http import HttpRequest
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet

from utilities.model_utils import ConfirmStatusChoices


def confirm_action(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet):
    updated = queryset.update(confirm_status=ConfirmStatusChoices.CONFIRMED)

    modeladmin.message_user(request,
                            f"{updated} مورد با موفقیت تایید شد",
                            messages.SUCCESS)

confirm_action.short_description = 'تایید موارد انتخاب شده'


def disprove_action(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet):
    updated = queryset.update(confirm_status=ConfirmStatusChoices.DISPROVED)

    modeladmin.message_user(request,
                            f"{updated} مورد با موفقیت رد شد",
                            messages.SUCCESS)

disprove_action.short_description = 'رد موارد انتخاب شده'
