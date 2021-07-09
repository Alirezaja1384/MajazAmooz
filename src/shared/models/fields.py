from django_bleach import forms as bleach_forms
from django_bleach.models import BleachField as BaseBleachField


class BleachField(BaseBleachField):
    """
    Customized bleach field to use BleachField form field
    as its form field in ModelForms
    """

    def formfield(self, **kwargs):
        """
        Makes field for ModelForm
        """

        # If field doesn't have any choice return BleachField
        if not self.choices:
            return bleach_forms.BleachField(
                label=self.verbose_name,
                max_length=self.max_length,
                allowed_tags=self.bleach_kwargs.get("tags"),
                allowed_attributes=self.bleach_kwargs.get("attributes"),
                allowed_styles=self.bleach_kwargs.get("styles"),
                allowed_protocols=self.bleach_kwargs.get("protocols"),
                strip_tags=self.bleach_kwargs.get("strip"),
                strip_comments=self.bleach_kwargs.get("strip_comments"),
            )

        return super(BleachField, self).formfield(**kwargs)
