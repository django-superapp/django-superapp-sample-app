from django.contrib import admin
from superapp.apps.admin_portal.helpers import SuperAppModelAdmin
from superapp.apps.admin_portal.sites import superapp_admin_site

from superapp.apps.sample_app.models import SampleModel


@admin.register(SampleModel, site=superapp_admin_site)
class SampleModelAdmin(SuperAppModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    list_per_page = 20
    ordering = ('-created_at',)
