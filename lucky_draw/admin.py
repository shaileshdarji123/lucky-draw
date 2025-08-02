from django.contrib import admin
from .models import Staff, CheckIn, Winner, EventSettings

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'day_1', 'created_at']
    list_filter = ['department', 'day_1', 'created_at']
    search_fields = ['name', 'department']
    readonly_fields = ['created_at']
    
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['staff', 'day', 'checked_in_at']
    list_filter = ['day', 'checked_in_at']
    search_fields = ['staff__name', 'staff__department']
    readonly_fields = ['checked_in_at']

@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ['staff', 'day', 'draw_order', 'drawn_at']
    list_filter = ['day', 'drawn_at']
    search_fields = ['staff__name', 'staff__department']
    readonly_fields = ['drawn_at']
    ordering = ['day', 'draw_order']

@admin.register(EventSettings)
class EventSettingsAdmin(admin.ModelAdmin):
    list_display = ['day1_date', 'day2_date', 'updated_at']
    readonly_fields = ['updated_at']
