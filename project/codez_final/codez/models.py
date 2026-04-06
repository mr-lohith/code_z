"""
codez/models.py  ── Complete merged model definitions
All models from both branches merged & de-duplicated.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum


# ── Choices ────────────────────────────────────────────────────────────────────
DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

BADGE_TYPE_CHOICES = [
    ('first_solve',  'First Solve'),
    ('streak_7',     '7-Day Streak'),
    ('streak_30',    '30-Day Streak'),
    ('points_100',   '100 Points'),
    ('points_500',   '500 Points'),
    ('points_1000',  '1000 Points'),
    ('top_10',       'Top 10 Rank'),
]

NOTIF_CHOICES = [
    ('upvote_q',         'Upvote on Question'),
    ('upvote_a',         'Upvote on Answer'),
    ('comment',          'New Comment'),
    ('follow',           'New Follower'),
    ('badge',            'Badge Earned'),
    ('accepted',         'Answer Accepted'),
    ('weekly_rank',      'Weekly Rank Update'),
    ('daily_reward',     'Daily Challenge Reward'),
    ('project_feedback', 'Project Feedback'),
    ('doubt_upvote',     'Doubt Answer Upvoted'),
    ('bug_reward',       'Bug Identification Reward'),
]

LANGUAGE_CHOICES = [
    ('python',     'Python'),
    ('javascript', 'JavaScript'),
    ('java',       'Java'),
    ('cpp',        'C++'),
    ('html',       'HTML'),
    ('go',         'Go'),
    ('rust',       'Rust'),
    ('typescript', 'TypeScript'),
    ('sql',        'SQL'),
]

LEVEL_CHOICES = [
    ('beginner',     'Beginner'),
    ('intermediate', 'Intermediate'),
    ('pro',          'Pro'),
]


# ── UserProfile ────────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio            = models.TextField(blank=True, max_length=300)
    github         = models.URLField(blank=True)
    website        = models.URLField(blank=True)
    location       = models.CharField(max_length=100, blank=True)
    college        = models.CharField(max_length=150, blank=True)
    avatar_seed    = models.CharField(max_length=60, blank=True)
    default_lang   = models.CharField(max_length=30, default='python')

    # Gamification
    points         = models.IntegerField(default=0)
    xp             = models.IntegerField(default=0)
    level          = models.IntegerField(default=1)
    streak_days    = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active    = models.DateField(null=True, blank=True)

    # Preferences
    theme          = models.CharField(max_length=10, default='dark')
    notif_upvotes  = models.BooleanField(default=True)
    notif_comments = models.BooleanField(default=True)
    notif_follows  = models.BooleanField(default=True)
    notif_weekly   = models.BooleanField(default=True)
    show_on_lb     = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)

    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-points']

    def __str__(self):
        return f"{self.user.username} – {self.points}pts"

    @property
    def rank(self):
        return UserProfile.objects.filter(points__gt=self.points, show_on_lb=True).count() + 1

    @property
    def xp_to_next_level(self):
        return self.level * 200

    @property
    def xp_percent(self):
        needed = self.xp_to_next_level
        return min(int((self.xp % needed) / needed * 100), 100) if needed else 100

    @property
    def solved_count(self):
        return Answer.objects.filter(author=self.user, is_accepted=True).count()

    @property
    def accuracy(self):
        total = Answer.objects.filter(author=self.user).count()
        if total == 0:
            return 0
        correct = Answer.objects.filter(author=self.user, is_accepted=True).count()
        return int(correct / total * 100)

    def update_streak(self):
        today = timezone.now().date()
        if self.last_active is None:
            self.streak_days = 1
        elif self.last_active == today:
            return
        elif self.last_active == today - timezone.timedelta(days=1):
            self.streak_days += 1
        else:
            self.streak_days = 1
        if self.streak_days > self.longest_streak:
            self.longest_streak = self.streak_days
        self.last_active = today
        self.save(update_fields=['streak_days', 'longest_streak', 'last_active'])

    def add_points(self, amount, xp_amount=None):
        self.points += amount
        self.xp     += xp_amount if xp_amount is not None else amount
        while self.xp >= self.level * 200:
            self.xp    -= self.level * 200
            self.level += 1
        self.save(update_fields=['points', 'xp', 'level'])
        self._check_badges()

    def _check_badges(self):
        milestones = {
            'points_100':  self.points >= 100,
            'points_500':  self.points >= 500,
            'points_1000': self.points >= 1000,
            'streak_7':    self.streak_days >= 7,
            'streak_30':   self.streak_days >= 30,
            'top_10':      self.rank <= 10,
        }
        for badge_type, condition in milestones.items():
            if condition:
                badge = Badge.objects.filter(badge_type=badge_type).first()
                if badge and not UserBadge.objects.filter(user=self.user, badge=badge).exists():
                    UserBadge.objects.create(user=self.user, badge=badge)
                    Notification.objects.create(
                        recipient=self.user, notif_type='badge',
                        message=f'You earned the "{badge.name}" badge!'
                    )


# ── Badge ──────────────────────────────────────────────────────────────────────
class Badge(models.Model):
    name        = models.CharField(max_length=80)
    description = models.CharField(max_length=200)
    icon        = models.CharField(max_length=60, default='fa-medal')
    color       = models.CharField(max_length=30, default='#FFD700')
    badge_type  = models.CharField(max_length=30, choices=BADGE_TYPE_CHOICES, unique=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge     = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} – {self.badge.name}"


# ── Tag ────────────────────────────────────────────────────────────────────────
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    def __str__(self):
        return self.name


# ── Question ───────────────────────────────────────────────────────────────────
class Question(models.Model):
    title      = models.CharField(max_length=200)
    body       = models.TextField()
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    tags       = models.ManyToManyField(Tag, blank=True, related_name='questions')
    language   = models.CharField(max_length=30, default='python')
    community  = models.CharField(max_length=80, default='c/SolveIt')
    views      = models.PositiveIntegerField(default=0)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def vote_count(self):
        result = self.votes.aggregate(total=Sum('value'))
        return result['total'] or 0

    @property
    def answer_count(self):
        return self.answers.count()

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class QuestionVote(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    value    = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])

    class Meta:
        unique_together = ('user', 'question')


# ── Answer ─────────────────────────────────────────────────────────────────────
class Answer(models.Model):
    question    = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    body        = models.TextField()
    code        = models.TextField(blank=True)
    language    = models.CharField(max_length=30, default='python')
    is_accepted = models.BooleanField(default=False)
    is_bug      = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_accepted', '-created_at']

    def __str__(self):
        return f"Answer by {self.author.username} on '{self.question.title}'"

    @property
    def vote_count(self):
        result = self.votes.aggregate(total=Sum('value'))
        return result['total'] or 0


class AnswerVote(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes')
    value  = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])

    class Meta:
        unique_together = ('user', 'answer')


# ── Comment ────────────────────────────────────────────────────────────────────
class Comment(models.Model):
    answer     = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body       = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username}"


# ── Bookmark ───────────────────────────────────────────────────────────────────
class Bookmark(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} bookmarked '{self.question.title}'"


# ── Follow ─────────────────────────────────────────────────────────────────────
class Follow(models.Model):
    follower   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


# ── Notification ───────────────────────────────────────────────────────────────
class Notification(models.Model):
    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notif_type = models.CharField(max_length=25, choices=NOTIF_CHOICES, default='upvote_a')
    message    = models.CharField(max_length=300)
    question   = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    answer     = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif for {self.recipient.username}: {self.message[:40]}"


# ── Learning Paths ─────────────────────────────────────────────────────────────
class LearningPath(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField()
    language    = models.CharField(max_length=30, default='python')
    level       = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner')
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['language', 'order']

    def __str__(self):
        return f"{self.title} ({self.language})"

    @property
    def step_count(self):
        return self.steps.count()


class LearningStep(models.Model):
    path     = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='steps')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='learning_steps')
    order    = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = (('path', 'question'),)

    def __str__(self):
        return f"{self.path.title} – step {self.order}"


class UserPathProgress(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='path_progress')
    path            = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='enrollments')
    completed_steps = models.ManyToManyField(LearningStep, blank=True, related_name='completions')
    enrolled_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'path'),)

    @property
    def percent_complete(self):
        total = self.path.steps.count()
        if total == 0:
            return 0
        return int(self.completed_steps.count() / total * 100)


# ── Daily Challenges ───────────────────────────────────────────────────────────
class DailyChallenge(models.Model):
    date         = models.DateField(unique=True)
    question     = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='daily_challenges')
    bonus_points = models.PositiveIntegerField(default=20)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Daily Challenge {self.date}"


class DailyChallengeCompletion(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_completions')
    challenge    = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'challenge'),)


# ── Project Forum ──────────────────────────────────────────────────────────────
class ProjectPost(models.Model):
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title       = models.CharField(max_length=200)
    description = models.TextField()
    code        = models.TextField(blank=True)
    language    = models.CharField(max_length=30, default='python')
    repo_url    = models.URLField(blank=True)
    demo_url    = models.URLField(blank=True)
    tags        = models.ManyToManyField(Tag, blank=True, related_name='projects')
    views       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class ProjectUpvote(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    project    = models.ForeignKey(ProjectPost, on_delete=models.CASCADE, related_name='upvotes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'project'),)


class ProjectFeedback(models.Model):
    project       = models.ForeignKey(ProjectPost, on_delete=models.CASCADE, related_name='feedbacks')
    author        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_feedbacks')
    body          = models.TextField()
    is_bug_report = models.BooleanField(default=False)
    upvotes       = models.ManyToManyField(User, blank=True, related_name='feedback_upvotes')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def upvote_count(self):
        return self.upvotes.count()


# ── Doubt Forum ────────────────────────────────────────────────────────────────
class DoubtThread(models.Model):
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doubt_threads')
    question    = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='doubt_threads')
    title       = models.CharField(max_length=200)
    body        = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DoubtReply(models.Model):
    thread      = models.ForeignKey(DoubtThread, on_delete=models.CASCADE, related_name='replies')
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doubt_replies')
    body        = models.TextField()
    is_accepted = models.BooleanField(default=False)
    upvotes     = models.ManyToManyField(User, blank=True, related_name='doubt_reply_upvotes')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    @property
    def upvote_count(self):
        return self.upvotes.count()
