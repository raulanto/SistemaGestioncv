from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils.translation import gettext_lazy as _
from unfold.admin import (
    ModelAdmin,
)
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    RelatedCheckboxFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .cuadrilla_admin import CuadrillaAdmin
from .element_admin import ElementoConstructivoAdmin
from .project_admin import ProyectoAdmin
from .punto_admin import PuntoControlAdmin
from .report_admin import ReporteAvanceAdmin
from .volume_admin import VolumenTerraceriaAdmin

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_fullwidth = True
    list_filter = [
        ("is_staff", BooleanRadioFilter),
        ("is_superuser", BooleanRadioFilter),
        ("is_active", BooleanRadioFilter),
        ("groups", RelatedCheckboxFilter),
    ]
    list_filter_submit = True
    list_filter_sheet = False

    compressed_fields = True
    list_display = [
        "display_header",
        "is_active",
        "display_staff",
        "display_superuser",
    ]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (("first_name", "last_name"), "email"),
                "classes": ["tab"],
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["tab"],
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login", "date_joined"),
                "classes": ["tab"],
            },
        ),
    )
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    readonly_fields = ["last_login", "date_joined"]
    show_full_result_count = False

    @display(description=_("User"))
    def display_header(self, instance: User):
        return instance.username

    @display(description=_("Staff"), boolean=True)
    def display_staff(self, instance: User):
        return instance.is_staff

    @display(description=_("Superuser"), boolean=True)
    def display_superuser(self, instance: User):
        return instance.is_superuser



@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


__all__ = ['ProyectoAdmin', 'ElementoConstructivoAdmin', 'PuntoControlAdmin', 'CuadrillaAdmin', "ReporteAvanceAdmin",
           "VolumenTerraceriaAdmin"]
