from django.contrib import admin
from .models import MortalityRate




@admin.register(MortalityRate)
class MortalityRateAdmin(admin.ModelAdmin):
    search_fields = ('age', )
    list_display = ('age', 'qx_percent', 'qx_value', 'px_percent', 'px_value', 'created_at')

