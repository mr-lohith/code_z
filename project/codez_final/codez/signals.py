from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Badge, UserBadge, QuestionVote, AnswerVote, Follow, Notification


# ── Auto-create UserProfile when a new User is created ───────────────────────
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'avatar_seed': instance.username}
        )
        # Award "First Solve" badge entry — actual award on first accepted answer
        # Seed default badges if they don't exist yet
        _seed_badges()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# ── Notify question author on upvote ─────────────────────────────────────────
@receiver(post_save, sender=QuestionVote)
def notify_question_upvote(sender, instance, created, **kwargs):
    if created and instance.value == 1:
        q = instance.question
        if q.author != instance.user:
            Notification.objects.create(
                recipient  = q.author,
                sender     = instance.user,
                notif_type = 'upvote_q',
                message    = f'{instance.user.username} upvoted your question "{q.title[:50]}"',
                question   = q,
            )
            # Award 2 pts to question author
            if hasattr(q.author, 'profile'):
                q.author.profile.add_points(2, xp_amount=2)


# ── Notify answer author on upvote ────────────────────────────────────────────
@receiver(post_save, sender=AnswerVote)
def notify_answer_upvote(sender, instance, created, **kwargs):
    if created and instance.value == 1:
        a = instance.answer
        if a.author != instance.user:
            Notification.objects.create(
                recipient  = a.author,
                sender     = instance.user,
                notif_type = 'upvote_a',
                message    = f'{instance.user.username} upvoted your answer on "{a.question.title[:40]}"',
                question   = a.question,
                answer     = a,
            )
            if hasattr(a.author, 'profile'):
                a.author.profile.add_points(2, xp_amount=2)


# ── Notify user on new follower ───────────────────────────────────────────────
@receiver(post_save, sender=Follow)
def notify_new_follower(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient  = instance.following,
            sender     = instance.follower,
            notif_type = 'follow',
            message    = f'{instance.follower.username} started following you!',
        )


# ── Helper: seed default badges ──────────────────────────────────────────────
def _seed_badges():
    defaults = [
        ('first_solve',  'First Blood',      'fa-fire',       '#EF4444', 'Solved your first problem!'),
        ('streak_7',     '7-Day Streak',      'fa-bolt',       '#F59E0B', 'Logged in 7 days in a row.'),
        ('streak_30',    '30-Day Legend',     'fa-crown',      '#6366f1', '30-day unbroken streak!'),
        ('points_100',   'Centurion',         'fa-star',       '#10B981', 'Earned 100 points.'),
        ('points_500',   'High Scorer',       'fa-trophy',     '#FFD700', 'Earned 500 points.'),
        ('points_1000',  'Elite Coder',       'fa-gem',        '#8b5cf6', 'Earned 1000 points.'),
        ('top_10',       'Top 10',            'fa-ranking-star','#FF6B35', 'Reached Global Top 10.'),
    ]
    for badge_type, name, icon, color, desc in defaults:
        Badge.objects.get_or_create(
            badge_type=badge_type,
            defaults={'name': name, 'icon': icon, 'color': color, 'description': desc}
        )
