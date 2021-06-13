from django.contrib.admin.decorators import register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from authentication.models import User
from utilities.templatetags.image_utils import image_tag


UserModel = get_user_model()


@register(UserModel)
class UserAdmin(BaseUserAdmin):

    def avatar_image_tag(self, obj: User):
        return image_tag(obj.avatar, str(obj), 50, 50, additional_styles='border-radius:50%;')
    avatar_image_tag.short_description = 'تصویر پروفایل'

    list_display_links = ('username',)
    list_display = ('avatar_image_tag', 'username', 'email',
                    'first_name', 'last_name', 'is_staff',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('سایر', {'fields': ('avatar', 'email_confirmed', )}),
    )
