from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from import_export.resources import ModelResource
from admin_panel.models import User, SupportRequest, Dispatcher, Post, MailingLog, Order, Settings


class CustomImportExport(ImportExportModelAdmin, ExportActionModelAdmin):
    pass


# setup import
class UserResource(ModelResource):
    class Meta:
        model = User
        import_id_fields = ('user_id',)


@admin.register(User)
class UserAdmin(CustomImportExport):
    resource_classes = [UserResource]
    list_display = ('user_id', 'fio', 'phone', 'payment_amount', 'refills_amount', 'created_at', 'last_activity')
    list_display_links = ('user_id',)


@admin.register(SupportRequest)
class SupportRequestAdmin(CustomImportExport):
    list_display = [field.name for field in SupportRequest._meta.fields]


@admin.register(Order)
class OrderAdmin(CustomImportExport):
    list_display = ['id', 'user', 'amount', 'total_price', 'is_paid', 'created_at', 'updated_at']
    exclude = ['station', 'product']


@admin.register(Dispatcher)
class DispatcherAdmin(CustomImportExport):
    list_display = [field.name for field in Dispatcher._meta.fields]


@admin.register(Post)
class OrderAdmin(CustomImportExport):
    list_display = [field.name for field in Post._meta.fields]
    list_editable = [field.name for field in Post._meta.fields if field.name != 'id' and field.name != 'created_at']


@admin.register(MailingLog)
class MailingLogAdmin(CustomImportExport):
    list_display = [field.name for field in MailingLog._meta.fields]


@admin.register(Settings)
class SettingsAdmin(CustomImportExport):
    list_display = [field.name for field in Settings._meta.fields]
    list_editable = ['card_data', 'discount_percent']


# sort models from admin.py by their registering (not alphabetically)
def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = list(app_dict.values())
    return app_list


admin.AdminSite.get_app_list = get_app_list
