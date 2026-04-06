"""
codez/views.py  ── Complete merged views
Covers: auth, home, questions, voting, bookmarks, search,
        leaderboard, notifications, follow, profile, settings,
        learning paths, daily challenges, project forum, doubt forum.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.text import slugify
from django import forms

from .models import (
    UserProfile, Question, Tag, Answer, AnswerVote, QuestionVote,
    Bookmark, Follow, Notification, Comment, UserBadge, Badge,
    LearningPath, LearningStep, UserPathProgress,
    DailyChallenge, DailyChallengeCompletion,
    ProjectPost, ProjectUpvote, ProjectFeedback,
    DoubtThread, DoubtReply,
)
from .signals import _seed_badges


# ── Forms ──────────────────────────────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'codez-input', 'placeholder': 'Username', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'codez-input', 'placeholder': 'Password', 'autocomplete': 'current-password'})
    )


class RegisterForm(UserCreationForm):
    email     = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'codez-input', 'placeholder': 'Email address'}))
    username  = forms.CharField(widget=forms.TextInput(attrs={'class': 'codez-input', 'placeholder': 'Username'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'codez-input', 'placeholder': 'Password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'codez-input', 'placeholder': 'Confirm Password'}))

    class Meta:
        model  = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# ── Helpers ────────────────────────────────────────────────────────────────────
def _get_profile(user):
    """Get or create UserProfile for the given user."""
    profile, _ = UserProfile.objects.get_or_create(
        user=user, defaults={'avatar_seed': user.username}
    )
    return profile


def _touch_streak(user):
    """Update the daily streak and award streak points."""
    p   = _get_profile(user)
    old = p.streak_days
    p.update_streak()
    if p.streak_days > old:
        p.add_points(5, xp_amount=5)


def _base_ctx(request):
    """Return context dict shared across all views."""
    profile      = _get_profile(request.user)
    unread_notif = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return {'profile': profile, 'unread_notif': unread_notif}


# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        _touch_streak(user)
        _seed_badges()
        return redirect(request.GET.get('next', 'home'))
    return render(request, 'codez/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        _touch_streak(user)
        _seed_badges()
        messages.success(request, f'Welcome to CodeZ, {user.username}!')
        return redirect('home')
    return render(request, 'codez/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ══════════════════════════════════════════════════════════════════════════════
# HOME FEED
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def home_view(request):
    q        = request.GET.get('q', '').strip()
    diff     = request.GET.get('diff', '')
    lang     = request.GET.get('lang', '')
    tag_slug = request.GET.get('tag', '')
    sort     = request.GET.get('sort', 'new')

    qs = Question.objects.select_related('author').prefetch_related('tags')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(tags__name__icontains=q)).distinct()
    if diff:
        qs = qs.filter(difficulty=diff)
    if lang:
        qs = qs.filter(language__icontains=lang)
    if tag_slug:
        qs = qs.filter(tags__slug=tag_slug)
    if sort == 'top':
        qs = qs.annotate(tv=Sum('votes__value')).order_by('-tv', '-created_at')
    elif sort == 'hot':
        qs = qs.annotate(ac=Count('answers')).order_by('-ac', '-views', '-created_at')
    else:
        qs = qs.order_by('-created_at')

    paginator      = Paginator(qs, 10)
    page           = paginator.get_page(request.GET.get('page', 1))
    bookmarked_ids = set(
        Bookmark.objects.filter(user=request.user, question__in=[p.id for p in page])
        .values_list('question_id', flat=True)
    )
    tags = Tag.objects.all()[:20]
    ctx  = _base_ctx(request)
    ctx.update({
        'page': page, 'bookmarked_ids': bookmarked_ids, 'tags': tags,
        'q': q, 'diff': diff, 'lang': lang, 'sort': sort, 'tag_slug': tag_slug,
    })
    return render(request, 'codez/home.html', ctx)


# ══════════════════════════════════════════════════════════════════════════════
# QUESTIONS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def question_view(request, pk=None):
    if pk:
        question = get_object_or_404(
            Question.objects.select_related('author')
            .prefetch_related('tags', 'answers__author', 'answers__comments__author'),
            pk=pk
        )
        question.increment_views()
    else:
        question = Question.objects.first()
        if not question:
            ctx = _base_ctx(request)
            ctx.update({'question': None, 'answers': []})
            return render(request, 'codez/question.html', ctx)

    answers      = question.answers.annotate(tv=Sum('votes__value')).order_by('-is_accepted', '-tv', '-created_at')
    user_q_vote  = QuestionVote.objects.filter(user=request.user, question=question).first()
    user_a_votes = {v.answer_id: v.value for v in AnswerVote.objects.filter(user=request.user, answer__question=question)}
    is_bookmarked = Bookmark.objects.filter(user=request.user, question=question).exists()
    ctx = _base_ctx(request)
    ctx.update({
        'question': question, 'answers': answers,
        'user_q_vote': user_q_vote.value if user_q_vote else 0,
        'user_a_votes': user_a_votes, 'is_bookmarked': is_bookmarked,
    })
    return render(request, 'codez/question.html', ctx)


@login_required
@require_POST
def submit_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)
    body     = request.POST.get('body', '').strip()
    code     = request.POST.get('code', '').strip()
    language = request.POST.get('language', 'python')
    if not body and not code:
        messages.error(request, 'Answer cannot be empty.')
        return redirect('question_detail', pk=pk)
    answer = Answer.objects.create(
        question=question, author=request.user,
        body=body, code=code, language=language
    )
    if question.author != request.user:
        Notification.objects.create(
            recipient=question.author, sender=request.user, notif_type='comment',
            message=f'{request.user.username} answered "{question.title[:50]}"',
            question=question, answer=answer
        )
    pts = {'easy': 10, 'medium': 25, 'hard': 50}.get(question.difficulty, 10)
    _get_profile(request.user).add_points(pts)
    # First solve badge
    if Answer.objects.filter(author=request.user).count() == 1:
        badge = Badge.objects.filter(badge_type='first_solve').first()
        if badge and not UserBadge.objects.filter(user=request.user, badge=badge).exists():
            UserBadge.objects.create(user=request.user, badge=badge)
            Notification.objects.create(
                recipient=request.user, notif_type='badge',
                message='You earned the "First Blood" badge!'
            )
    messages.success(request, 'Answer submitted!')
    return redirect('question_detail', pk=pk)


@login_required
@require_POST
def accept_answer(request, answer_pk):
    answer = get_object_or_404(Answer, pk=answer_pk)
    if request.user != answer.question.author:
        return JsonResponse({'error': 'Not authorised'}, status=403)
    answer.question.answers.update(is_accepted=False)
    answer.is_accepted = not answer.is_accepted
    answer.save()
    if answer.is_accepted:
        _get_profile(answer.author).add_points(15, xp_amount=20)
        Notification.objects.create(
            recipient=answer.author, sender=request.user, notif_type='accepted',
            message=f'Your answer was accepted on "{answer.question.title[:50]}"',
            question=answer.question, answer=answer
        )
    return JsonResponse({'accepted': answer.is_accepted})


# ══════════════════════════════════════════════════════════════════════════════
# VOTES (AJAX)
# ══════════════════════════════════════════════════════════════════════════════
@login_required
@require_POST
def vote_question(request, pk):
    question  = get_object_or_404(Question, pk=pk)
    data      = json.loads(request.body)
    direction = int(data.get('direction', 1))
    existing  = QuestionVote.objects.filter(user=request.user, question=question).first()
    if existing:
        if existing.value == direction:
            existing.delete()
            new_vote = 0
        else:
            existing.value = direction
            existing.save()
            new_vote = direction
    else:
        QuestionVote.objects.create(user=request.user, question=question, value=direction)
        new_vote = direction
    total = question.votes.aggregate(t=Sum('value'))['t'] or 0
    return JsonResponse({'total': total, 'user_vote': new_vote})


@login_required
@require_POST
def vote_answer(request, pk):
    answer    = get_object_or_404(Answer, pk=pk)
    data      = json.loads(request.body)
    direction = int(data.get('direction', 1))
    existing  = AnswerVote.objects.filter(user=request.user, answer=answer).first()
    if existing:
        if existing.value == direction:
            existing.delete()
            new_vote = 0
        else:
            existing.value = direction
            existing.save()
            new_vote = direction
    else:
        AnswerVote.objects.create(user=request.user, answer=answer, value=direction)
        new_vote = direction
    total = answer.votes.aggregate(t=Sum('value'))['t'] or 0
    return JsonResponse({'total': total, 'user_vote': new_vote})


# ══════════════════════════════════════════════════════════════════════════════
# BOOKMARKS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
@require_POST
def bookmark_toggle(request, pk):
    question    = get_object_or_404(Question, pk=pk)
    bm, created = Bookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bm.delete()
        return JsonResponse({'bookmarked': False})
    return JsonResponse({'bookmarked': True})


@login_required
def bookmarks_view(request):
    bookmarks = (
        Bookmark.objects
        .filter(user=request.user)
        .select_related('question__author')
        .prefetch_related('question__tags')
        .order_by('-created_at')
    )
    ctx = _base_ctx(request)
    ctx['bookmarks'] = bookmarks
    return render(request, 'codez/bookmarks.html', ctx)


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def search_view(request):
    q       = request.GET.get('q', '').strip()
    results = []
    users   = []
    if q:
        results = (
            Question.objects
            .filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(tags__name__icontains=q))
            .distinct().select_related('author').prefetch_related('tags')[:30]
        )
        users = User.objects.filter(username__icontains=q).select_related('profile')[:10]
    ctx = _base_ctx(request)
    ctx.update({'q': q, 'results': results, 'users': users})
    return render(request, 'codez/search.html', ctx)


# ══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def leaderboard_view(request):
    tab = request.GET.get('tab', 'global')
    if tab == 'friends':
        fids     = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        profiles = (
            UserProfile.objects
            .filter(user_id__in=list(fids) + [request.user.id], show_on_lb=True)
            .select_related('user').order_by('-points')
        )
    elif tab == 'weekly':
        week_ago = (timezone.now() - timezone.timedelta(days=7)).date()
        profiles = (
            UserProfile.objects
            .filter(show_on_lb=True, last_active__gte=week_ago)
            .select_related('user').order_by('-points')[:50]
        )
    else:
        profiles = (
            UserProfile.objects
            .filter(show_on_lb=True)
            .select_related('user').order_by('-points')[:50]
        )
    ranked = [{'rank': i, 'profile': p} for i, p in enumerate(profiles, 1)]
    ctx    = _base_ctx(request)
    ctx.update({'ranked': ranked, 'tab': tab})
    return render(request, 'codez/leaderboard.html', ctx)


# ══════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(recipient=request.user).select_related('sender', 'question')[:50]
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    ctx = _base_ctx(request)
    ctx.update({'notifs': notifs, 'unread_notif': 0})
    return render(request, 'codez/notifications.html', ctx)


@login_required
@require_POST
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'ok': True})


@login_required
def notif_count_api(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


# ══════════════════════════════════════════════════════════════════════════════
# FOLLOW
# ══════════════════════════════════════════════════════════════════════════════
@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        return JsonResponse({'following': False, 'count': target.followers.count()})
    return JsonResponse({'following': True, 'count': target.followers.count()})


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def profile_view(request, username=None):
    profile_user    = get_object_or_404(User, username=username) if username else request.user
    prof            = _get_profile(profile_user)
    questions       = Question.objects.filter(author=profile_user).order_by('-created_at')[:10]
    answers         = Answer.objects.filter(author=profile_user).select_related('question').order_by('-created_at')[:10]
    badges          = UserBadge.objects.filter(user=profile_user).select_related('badge')
    bookmarks       = Bookmark.objects.filter(user=profile_user).select_related('question').order_by('-created_at')[:10]
    is_following    = (
        Follow.objects.filter(follower=request.user, following=profile_user).exists()
        if request.user != profile_user else False
    )
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    ctx = _base_ctx(request)
    ctx.update({
        'profile_user': profile_user, 'prof': prof,
        'questions': questions, 'answers': answers,
        'badges': badges, 'bookmarks': bookmarks,
        'is_following': is_following,
        'followers_count': followers_count, 'following_count': following_count,
    })
    return render(request, 'codez/profile.html', ctx)


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def settings_view(request):
    profile = _get_profile(request.user)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'update_profile':
            u            = request.user
            u.first_name = request.POST.get('first_name', u.first_name).strip()
            u.last_name  = request.POST.get('last_name', u.last_name).strip()
            new_email    = request.POST.get('email', '').strip()
            if new_email:
                u.email = new_email
            u.save()
            profile.bio          = request.POST.get('bio', '').strip()[:300]
            profile.github       = request.POST.get('github', '').strip()
            profile.website      = request.POST.get('website', '').strip()
            profile.location     = request.POST.get('location', '').strip()
            profile.college      = request.POST.get('college', '').strip()
            profile.default_lang = request.POST.get('default_lang', 'python')
            profile.save()
            messages.success(request, 'Profile updated successfully!')
        elif action == 'change_password':
            current = request.POST.get('current_password', '')
            new_pw  = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')
            if not request.user.check_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully!')
        elif action == 'update_notifications':
            profile.notif_upvotes  = 'notif_upvotes'  in request.POST
            profile.notif_comments = 'notif_comments' in request.POST
            profile.notif_follows  = 'notif_follows'  in request.POST
            profile.notif_weekly   = 'notif_weekly'   in request.POST
            profile.save()
            messages.success(request, 'Notification preferences saved!')
        elif action == 'update_privacy':
            profile.public_profile = 'public_profile' in request.POST
            profile.show_on_lb     = 'show_on_lb'     in request.POST
            profile.save()
            messages.success(request, 'Privacy settings saved!')
        elif action == 'update_appearance':
            profile.theme = request.POST.get('theme', 'dark')
            profile.save()
            messages.success(request, 'Appearance settings saved!')
        return redirect('settings')
    ctx = _base_ctx(request)
    return render(request, 'codez/settings.html', ctx)


# ══════════════════════════════════════════════════════════════════════════════
# LEARNING PATHS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def learning_paths_view(request):
    language = request.GET.get('lang', '')
    level    = request.GET.get('level', '')
    qs = LearningPath.objects.prefetch_related('steps')
    if language:
        qs = qs.filter(language=language)
    if level:
        qs = qs.filter(level=level)

    paths_with_progress = []
    for path in qs:
        progress, _ = UserPathProgress.objects.get_or_create(user=request.user, path=path)
        paths_with_progress.append({'path': path, 'progress': progress})

    ctx = _base_ctx(request)
    ctx.update({'paths_with_progress': paths_with_progress, 'language': language, 'level': level})
    return render(request, 'codez/learning_paths.html', ctx)


@login_required
def learning_path_detail(request, pk):
    path     = get_object_or_404(LearningPath, pk=pk)
    steps    = path.steps.select_related('question')
    progress, _ = UserPathProgress.objects.get_or_create(user=request.user, path=path)
    completed_ids = set(progress.completed_steps.values_list('id', flat=True))
    ctx = _base_ctx(request)
    ctx.update({'path': path, 'steps': steps, 'progress': progress, 'completed_ids': completed_ids})
    return render(request, 'codez/learning_path_detail.html', ctx)


@login_required
@require_POST
def complete_learning_step(request, step_pk):
    step     = get_object_or_404(LearningStep, pk=step_pk)
    progress, _ = UserPathProgress.objects.get_or_create(user=request.user, path=step.path)
    already_done = step in progress.completed_steps.all()
    if not already_done:
        progress.completed_steps.add(step)
        _get_profile(request.user).add_points(10, xp_amount=15)
    return JsonResponse({
        'completed': True,
        'already_done': already_done,
        'percent': progress.percent_complete,
    })


# ══════════════════════════════════════════════════════════════════════════════
# DAILY CHALLENGES
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def daily_challenge_view(request):
    today     = timezone.now().date()
    challenge = DailyChallenge.objects.filter(date=today).select_related('question').first()
    completed = False
    if challenge:
        completed = DailyChallengeCompletion.objects.filter(user=request.user, challenge=challenge).exists()
    past_challenges = DailyChallenge.objects.filter(date__lt=today).select_related('question')[:7]
    ctx = _base_ctx(request)
    ctx.update({'challenge': challenge, 'completed': completed, 'past_challenges': past_challenges})
    return render(request, 'codez/daily_challenge.html', ctx)


@login_required
@require_POST
def complete_daily_challenge(request, pk):
    challenge = get_object_or_404(DailyChallenge, pk=pk)
    today     = timezone.now().date()
    if challenge.date != today:
        return JsonResponse({'error': 'Challenge has expired.'}, status=400)
    _, created = DailyChallengeCompletion.objects.get_or_create(user=request.user, challenge=challenge)
    if created:
        prof = _get_profile(request.user)
        prof.add_points(challenge.bonus_points, xp_amount=challenge.bonus_points)
        _touch_streak(request.user)
        Notification.objects.create(
            recipient=request.user, notif_type='daily_reward',
            message=f"You earned {challenge.bonus_points} bonus points for today's challenge!"
        )
    return JsonResponse({'completed': True, 'already_done': not created})


# ══════════════════════════════════════════════════════════════════════════════
# PROJECT FORUM
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def project_forum_view(request):
    lang = request.GET.get('lang', '')
    sort = request.GET.get('sort', 'new')
    qs   = ProjectPost.objects.select_related('author').prefetch_related('tags', 'upvotes')
    if lang:
        qs = qs.filter(language=lang)
    if sort == 'top':
        qs = qs.annotate(upc=Count('upvotes')).order_by('-upc', '-created_at')
    elif sort == 'hot':
        qs = qs.order_by('-views', '-created_at')
    else:
        qs = qs.order_by('-created_at')
    paginator = Paginator(qs, 12)
    page      = paginator.get_page(request.GET.get('page', 1))
    ctx = _base_ctx(request)
    ctx.update({'page': page, 'lang': lang, 'sort': sort})
    return render(request, 'codez/project_forum.html', ctx)


@login_required
def project_detail_view(request, pk):
    project = get_object_or_404(
        ProjectPost.objects.select_related('author')
        .prefetch_related('tags', 'feedbacks__author', 'feedbacks__upvotes'),
        pk=pk
    )
    project.increment_views()
    feedbacks  = project.feedbacks.all()
    is_upvoted = ProjectUpvote.objects.filter(user=request.user, project=project).exists()
    ctx = _base_ctx(request)
    ctx.update({'project': project, 'feedbacks': feedbacks, 'is_upvoted': is_upvoted})
    return render(request, 'codez/project_detail.html', ctx)


@login_required
def submit_project_view(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        code        = request.POST.get('code', '').strip()
        language    = request.POST.get('language', 'python')
        repo_url    = request.POST.get('repo_url', '').strip()
        demo_url    = request.POST.get('demo_url', '').strip()
        tag_names   = [t.strip() for t in request.POST.get('tags', '').split(',') if t.strip()]
        if not title or not description:
            messages.error(request, 'Title and description are required.')
        else:
            project = ProjectPost.objects.create(
                author=request.user, title=title, description=description,
                code=code, language=language, repo_url=repo_url, demo_url=demo_url,
            )
            for tag_name in tag_names[:5]:
                tag, _ = Tag.objects.get_or_create(name=tag_name, defaults={'slug': slugify(tag_name)})
                project.tags.add(tag)
            _get_profile(request.user).add_points(15, xp_amount=20)
            messages.success(request, 'Project submitted successfully!')
            return redirect('project_detail', pk=project.pk)
    ctx = _base_ctx(request)
    return render(request, 'codez/submit_project.html', ctx)


@login_required
@require_POST
def project_upvote_toggle(request, pk):
    project         = get_object_or_404(ProjectPost, pk=pk)
    upvote, created = ProjectUpvote.objects.get_or_create(user=request.user, project=project)
    if not created:
        upvote.delete()
        return JsonResponse({'upvoted': False, 'count': project.upvotes.count()})
    if project.author != request.user:
        Notification.objects.create(
            recipient=project.author, sender=request.user, notif_type='project_feedback',
            message=f'{request.user.username} upvoted your project "{project.title[:40]}"'
        )
    return JsonResponse({'upvoted': True, 'count': project.upvotes.count()})


@login_required
@require_POST
def submit_project_feedback(request, pk):
    project       = get_object_or_404(ProjectPost, pk=pk)
    body          = request.POST.get('body', '').strip()
    is_bug_report = request.POST.get('is_bug_report') == 'on'
    if not body:
        messages.error(request, 'Feedback cannot be empty.')
        return redirect('project_detail', pk=pk)
    feedback = ProjectFeedback.objects.create(
        project=project, author=request.user, body=body, is_bug_report=is_bug_report
    )
    if project.author != request.user:
        Notification.objects.create(
            recipient=project.author, sender=request.user, notif_type='project_feedback',
            message=f'{request.user.username} {"reported a bug" if is_bug_report else "gave feedback"} on your project "{project.title[:40]}"'
        )
    if is_bug_report:
        _get_profile(request.user).add_points(10, xp_amount=10)
        Notification.objects.create(
            recipient=request.user, notif_type='bug_reward',
            message='You earned 10 points for reporting a bug!'
        )
    messages.success(request, 'Feedback submitted!')
    return redirect('project_detail', pk=pk)


@login_required
@require_POST
def upvote_project_feedback(request, pk):
    feedback = get_object_or_404(ProjectFeedback, pk=pk)
    if request.user in feedback.upvotes.all():
        feedback.upvotes.remove(request.user)
        upvoted = False
    else:
        feedback.upvotes.add(request.user)
        upvoted = True
        if feedback.author != request.user:
            _get_profile(feedback.author).add_points(5, xp_amount=5)
            Notification.objects.create(
                recipient=feedback.author, sender=request.user, notif_type='bug_reward',
                message='Your feedback was upvoted! +5 points'
            )
    return JsonResponse({'upvoted': upvoted, 'count': feedback.upvote_count})


# ══════════════════════════════════════════════════════════════════════════════
# DOUBT FORUM
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def doubt_forum_view(request):
    question_pk = request.GET.get('question')
    qs = DoubtThread.objects.select_related('author', 'question').prefetch_related('replies')
    if question_pk:
        qs = qs.filter(question_id=question_pk)
    paginator = Paginator(qs, 15)
    page      = paginator.get_page(request.GET.get('page', 1))
    ctx = _base_ctx(request)
    ctx['page'] = page
    return render(request, 'codez/doubt_forum.html', ctx)


@login_required
def doubt_thread_view(request, pk):
    thread = get_object_or_404(
        DoubtThread.objects.select_related('author', 'question')
        .prefetch_related('replies__author', 'replies__upvotes'),
        pk=pk
    )
    replies = sorted(
        thread.replies.all(),
        key=lambda r: (-r.is_accepted, -r.upvote_count, r.created_at.timestamp())
    )
    ctx = _base_ctx(request)
    ctx.update({'thread': thread, 'replies': replies})
    return render(request, 'codez/doubt_thread.html', ctx)


@login_required
@require_POST
def post_doubt_thread(request):
    question_pk = request.POST.get('question_pk')
    title       = request.POST.get('title', '').strip()
    body        = request.POST.get('body', '').strip()
    question    = get_object_or_404(Question, pk=question_pk) if question_pk else None
    if not title or not body or not question:
        messages.error(request, 'Title, body, and a linked question are required.')
        return redirect('doubt_forum')
    thread = DoubtThread.objects.create(author=request.user, question=question, title=title, body=body)
    messages.success(request, 'Doubt posted!')
    return redirect('doubt_thread', pk=thread.pk)


@login_required
@require_POST
def post_doubt_reply(request, thread_pk):
    thread = get_object_or_404(DoubtThread, pk=thread_pk)
    body   = request.POST.get('body', '').strip()
    if not body:
        messages.error(request, 'Reply cannot be empty.')
        return redirect('doubt_thread', pk=thread_pk)
    reply = DoubtReply.objects.create(thread=thread, author=request.user, body=body)
    if thread.author != request.user:
        Notification.objects.create(
            recipient=thread.author, sender=request.user, notif_type='comment',
            message=f'{request.user.username} replied to your doubt: "{thread.title[:50]}"'
        )
    messages.success(request, 'Reply posted!')
    return redirect('doubt_thread', pk=thread_pk)


@login_required
@require_POST
def upvote_doubt_reply(request, pk):
    reply = get_object_or_404(DoubtReply, pk=pk)
    if request.user in reply.upvotes.all():
        reply.upvotes.remove(request.user)
        upvoted = False
    else:
        reply.upvotes.add(request.user)
        upvoted = True
        if reply.author != request.user:
            _get_profile(reply.author).add_points(3, xp_amount=3)
            Notification.objects.create(
                recipient=reply.author, sender=request.user, notif_type='doubt_upvote',
                message='Your doubt reply was upvoted! +3 points'
            )
    return JsonResponse({'upvoted': upvoted, 'count': reply.upvote_count})


@login_required
@require_POST
def accept_doubt_reply(request, pk):
    reply = get_object_or_404(DoubtReply, pk=pk)
    if request.user != reply.thread.author:
        return JsonResponse({'error': 'Not authorised'}, status=403)
    reply.thread.replies.update(is_accepted=False)
    reply.is_accepted = not reply.is_accepted
    reply.save()
    if reply.is_accepted:
        reply.thread.is_resolved = True
        reply.thread.save(update_fields=['is_resolved'])
        _get_profile(reply.author).add_points(10, xp_amount=15)
        Notification.objects.create(
            recipient=reply.author, sender=request.user, notif_type='accepted',
            message='Your reply was accepted as the best answer!'
        )
    return JsonResponse({'accepted': reply.is_accepted})
