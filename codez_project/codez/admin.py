from django.contrib import admin
from .models import UserProfile, Problem

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'problems_solved', 'streak', 'is_online']
    search_fields = ['user__username', 'user__email']

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'upvotes', 'acceptance_rate', 'is_premium']
    list_filter = ['difficulty', 'is_premium']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
