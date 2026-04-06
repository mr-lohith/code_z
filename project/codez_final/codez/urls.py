"""
codez/urls.py  ── All URL patterns (merged + new features)
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path('',              views.home_view,    name='home'),
    path('login/',        views.login_view,   name='login'),
    path('register/',     views.register_view, name='register'),
    path('logout/',       views.logout_view,  name='logout'),

    # ── Profile & Social ──────────────────────────────────────────────────────
    path('profile/',                    views.profile_view,   name='my_profile'),
    path('profile/<str:username>/',     views.profile_view,   name='user_profile'),
    path('follow/<str:username>/',      views.follow_toggle,  name='follow_toggle'),

    # ── Questions ─────────────────────────────────────────────────────────────
    path('question/',                       views.question_view,   name='question'),
    path('question/<int:pk>/',              views.question_view,   name='question_detail'),
    path('question/<int:pk>/answer/',       views.submit_answer,   name='submit_answer'),
    path('answer/<int:answer_pk>/accept/',  views.accept_answer,   name='accept_answer'),

    # ── Votes (AJAX) ──────────────────────────────────────────────────────────
    path('api/vote/question/<int:pk>/',  views.vote_question,  name='vote_question'),
    path('api/vote/answer/<int:pk>/',    views.vote_answer,    name='vote_answer'),

    # ── Bookmarks ─────────────────────────────────────────────────────────────
    path('api/bookmark/<int:pk>/',  views.bookmark_toggle, name='bookmark_toggle'),
    path('bookmarks/',              views.bookmarks_view,  name='bookmarks'),

    # ── Search ────────────────────────────────────────────────────────────────
    path('search/', views.search_view, name='search'),

    # ── Leaderboard & Settings ────────────────────────────────────────────────
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('settings/',    views.settings_view,    name='settings'),

    # ── Notifications ─────────────────────────────────────────────────────────
    path('notifications/',              views.notifications_view,     name='notifications'),
    path('api/notif/<int:pk>/read/',    views.mark_notification_read, name='notif_read'),
    path('api/notif/count/',            views.notif_count_api,        name='notif_count'),

    # ── Learning Paths ────────────────────────────────────────────────────────
    path('learn/',                              views.learning_paths_view,   name='learning_paths'),
    path('learn/<int:pk>/',                     views.learning_path_detail,  name='learning_path_detail'),
    path('api/learn/step/<int:step_pk>/done/',  views.complete_learning_step, name='complete_learning_step'),

    # ── Daily Challenge ───────────────────────────────────────────────────────
    path('daily/',              views.daily_challenge_view,     name='daily_challenge'),
    path('daily/<int:pk>/complete/', views.complete_daily_challenge, name='complete_daily_challenge'),

    # ── Project Forum ─────────────────────────────────────────────────────────
    # IMPORTANT: 'submit/' must be declared before '<int:pk>/' so Django does
    # not try to cast the string "submit" to an integer.
    path('projects/',                            views.project_forum_view,       name='project_forum'),
    path('projects/submit/',                     views.submit_project_view,      name='submit_project'),
    path('projects/<int:pk>/',                   views.project_detail_view,      name='project_detail'),
    path('api/projects/<int:pk>/upvote/',        views.project_upvote_toggle,    name='project_upvote'),
    path('api/projects/<int:pk>/feedback/',      views.submit_project_feedback,  name='project_feedback'),
    path('api/feedback/<int:pk>/upvote/',        views.upvote_project_feedback,  name='upvote_feedback'),

    # ── Doubt Forum ───────────────────────────────────────────────────────────
    path('doubts/',                        views.doubt_forum_view,    name='doubt_forum'),
    path('doubts/new/',                    views.post_doubt_thread,   name='post_doubt'),
    path('doubts/<int:pk>/',               views.doubt_thread_view,   name='doubt_thread'),
    path('doubts/<int:thread_pk>/reply/',  views.post_doubt_reply,    name='post_doubt_reply'),
    path('api/doubt-reply/<int:pk>/upvote/',  views.upvote_doubt_reply,  name='upvote_doubt_reply'),
    path('api/doubt-reply/<int:pk>/accept/',  views.accept_doubt_reply,  name='accept_doubt_reply'),
]
