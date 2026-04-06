"""
codez/admin.py  ─── Full admin configuration for every CodeZ model
"""
from django.contrib import admin
from .models import (
    UserProfile, Badge, UserBadge, Tag,
    Question, QuestionVote,
    Answer, AnswerVote, Comment,
    Bookmark, Follow, Notification,
    LearningPath, LearningStep, UserPathProgress,
    DailyChallenge, DailyChallengeCompletion,
    ProjectPost, ProjectUpvote, ProjectFeedback,
    DoubtThread, DoubtReply,
)


# ── Inlines ────────────────────────────────────────────────────────────────────
class AnswerInline(admin.TabularInline):
    model           = Answer
    extra           = 0
    fields          = ['author', 'is_accepted', 'is_bug', 'language', 'created_at']
    readonly_fields = ['created_at']


class LearningStepInline(admin.TabularInline):
    model  = LearningStep
    extra  = 1
    fields = ['order', 'question']


class ProjectFeedbackInline(admin.TabularInline):
    model           = ProjectFeedback
    extra           = 0
    fields          = ['author', 'is_bug_report', 'created_at']
    readonly_fields = ['created_at']


class DoubtReplyInline(admin.TabularInline):
    model           = DoubtReply
    extra           = 0
    fields          = ['author', 'is_accepted', 'created_at']
    readonly_fields = ['created_at']


# ── UserProfile ────────────────────────────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display    = ['user', 'points', 'xp', 'level', 'streak_days', 'show_on_lb', 'theme']
    list_filter     = ['level', 'default_lang', 'show_on_lb', 'public_profile', 'theme']
    search_fields   = ['user__username', 'user__email', 'location', 'college']
    readonly_fields = ['rank', 'xp_percent', 'solved_count', 'accuracy', 'created_at']
    fieldsets = (
        ('Account',      {'fields': ('user', 'avatar_seed', 'bio', 'location', 'college', 'default_lang')}),
        ('Links',        {'fields': ('github', 'website')}),
        ('Gamification', {'fields': ('points', 'xp', 'level', 'streak_days', 'longest_streak', 'last_active')}),
        ('Read-only',    {'fields': ('rank', 'xp_percent', 'solved_count', 'accuracy', 'created_at')}),
        ('Preferences',  {'fields': ('theme', 'show_on_lb', 'public_profile',
                                     'notif_upvotes', 'notif_comments', 'notif_follows', 'notif_weekly')}),
    )


# ── Badges ─────────────────────────────────────────────────────────────────────
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display  = ['name', 'badge_type', 'icon', 'color']
    search_fields = ['name', 'badge_type']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display  = ['user', 'badge', 'earned_at']
    list_filter   = ['badge']
    search_fields = ['user__username', 'badge__name']


# ── Tag ────────────────────────────────────────────────────────────────────────
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


# ── Questions ──────────────────────────────────────────────────────────────────
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display      = ['title', 'author', 'difficulty', 'language', 'views', 'vote_count', 'answer_count', 'created_at']
    list_filter       = ['difficulty', 'language', 'is_premium', 'community']
    search_fields     = ['title', 'body', 'author__username']
    filter_horizontal = ['tags']
    readonly_fields   = ['vote_count', 'answer_count', 'views', 'created_at', 'updated_at']
    inlines           = [AnswerInline]


@admin.register(QuestionVote)
class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'value']
    list_filter  = ['value']


# ── Answers ────────────────────────────────────────────────────────────────────
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display    = ['author', 'question', 'is_accepted', 'is_bug', 'vote_count', 'created_at']
    list_filter     = ['is_accepted', 'is_bug', 'language']
    search_fields   = ['author__username', 'question__title', 'body']
    readonly_fields = ['vote_count', 'created_at', 'updated_at']


@admin.register(AnswerVote)
class AnswerVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'value']
    list_filter  = ['value']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ['author', 'answer', 'created_at']
    search_fields = ['author__username', 'body']


# ── Social ─────────────────────────────────────────────────────────────────────
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display  = ['user', 'question', 'created_at']
    search_fields = ['user__username', 'question__title']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display  = ['follower', 'following', 'created_at']
    search_fields = ['follower__username', 'following__username']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'sender', 'notif_type', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'is_read']
    search_fields = ['recipient__username', 'message']
    actions       = ['mark_all_read']

    def mark_all_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_all_read.short_description = 'Mark selected notifications as read'


# ── Learning Paths ─────────────────────────────────────────────────────────────
@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display  = ['title', 'language', 'level', 'order', 'step_count', 'created_at']
    list_filter   = ['language', 'level']
    search_fields = ['title', 'description']
    inlines       = [LearningStepInline]


@admin.register(UserPathProgress)
class UserPathProgressAdmin(admin.ModelAdmin):
    list_display      = ['user', 'path', 'percent_complete', 'enrolled_at']
    search_fields     = ['user__username', 'path__title']
    readonly_fields   = ['percent_complete', 'enrolled_at']
    filter_horizontal = ['completed_steps']


# ── Daily Challenges ───────────────────────────────────────────────────────────
@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display  = ['date', 'question', 'bonus_points']
    list_filter   = ['date']
    search_fields = ['question__title']


@admin.register(DailyChallengeCompletion)
class DailyChallengeCompletionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'challenge', 'completed_at']
    list_filter   = ['challenge__date']
    search_fields = ['user__username']


# ── Projects ───────────────────────────────────────────────────────────────────
@admin.register(ProjectPost)
class ProjectPostAdmin(admin.ModelAdmin):
    list_display      = ['title', 'author', 'language', 'views', 'created_at']
    list_filter       = ['language']
    search_fields     = ['title', 'description', 'author__username']
    filter_horizontal = ['tags']
    readonly_fields   = ['views', 'created_at', 'updated_at']
    inlines           = [ProjectFeedbackInline]


@admin.register(ProjectFeedback)
class ProjectFeedbackAdmin(admin.ModelAdmin):
    list_display    = ['author', 'project', 'is_bug_report', 'upvote_count', 'created_at']
    list_filter     = ['is_bug_report']
    search_fields   = ['author__username', 'body']
    readonly_fields = ['upvote_count']


# ── Doubt Forum ────────────────────────────────────────────────────────────────
@admin.register(DoubtThread)
class DoubtThreadAdmin(admin.ModelAdmin):
    list_display  = ['title', 'author', 'question', 'is_resolved', 'created_at']
    list_filter   = ['is_resolved']
    search_fields = ['title', 'body', 'author__username']
    inlines       = [DoubtReplyInline]


@admin.register(DoubtReply)
class DoubtReplyAdmin(admin.ModelAdmin):
    list_display    = ['author', 'thread', 'is_accepted', 'upvote_count', 'created_at']
    list_filter     = ['is_accepted']
    search_fields   = ['author__username', 'body']
    readonly_fields = ['upvote_count']
