from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'coach', 'sport')
    list_filter = ('role', 'sport')
    search_fields = ('user__username', 'user__email', 'sport')
    
    # Organize fields - Coach assignment only makes sense if role is Athlete
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'role', 'gender', 'date_of_birth')
        }),
        ('Athletic Data', {
            'fields': ('sport', 'height_cm', 'weight_kg')
        }),
        ('Coaching', {
            'fields': ('coach',),
            'description': 'Assign a coach here. Only valid for Athletes.'
        }),
    )

admin.site.register(UserProfile, UserProfileAdmin)
