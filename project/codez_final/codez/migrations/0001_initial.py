from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Badge
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name',        models.CharField(max_length=80)),
                ('description', models.CharField(max_length=200)),
                ('icon',        models.CharField(default='fa-medal', max_length=60)),
                ('color',       models.CharField(default='#FFD700', max_length=30)),
                ('badge_type',  models.CharField(choices=[
                    ('first_solve','First Solve'),('streak_7','7-Day Streak'),
                    ('streak_30','30-Day Streak'),('points_100','100 Points'),
                    ('points_500','500 Points'),('points_1000','1000 Points'),
                    ('top_10','Top 10 Rank')], max_length=30, unique=True)),
            ],
        ),
        # Tag
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id',   models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(max_length=60, unique=True)),
            ],
        ),
        # UserProfile
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id',             models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio',            models.TextField(blank=True, max_length=300)),
                ('github',         models.URLField(blank=True)),
                ('website',        models.URLField(blank=True)),
                ('location',       models.CharField(blank=True, max_length=100)),
                ('college',        models.CharField(blank=True, max_length=150)),
                ('avatar_seed',    models.CharField(blank=True, max_length=60)),
                ('default_lang',   models.CharField(default='python', max_length=30)),
                ('points',         models.IntegerField(default=0)),
                ('xp',             models.IntegerField(default=0)),
                ('level',          models.IntegerField(default=1)),
                ('streak_days',    models.IntegerField(default=0)),
                ('longest_streak', models.IntegerField(default=0)),
                ('last_active',    models.DateField(blank=True, null=True)),
                ('theme',          models.CharField(default='light', max_length=10)),
                ('notif_upvotes',  models.BooleanField(default=True)),
                ('notif_comments', models.BooleanField(default=True)),
                ('notif_follows',  models.BooleanField(default=True)),
                ('notif_weekly',   models.BooleanField(default=True)),
                ('show_on_lb',     models.BooleanField(default=True)),
                ('public_profile', models.BooleanField(default=True)),
                ('created_at',     models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-points']},
        ),
        # UserBadge
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id',        models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earned_at', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codez.badge')),
                ('user',  models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='badges', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('user', 'badge')}},
        ),
        # Question
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title',      models.CharField(max_length=200)),
                ('body',       models.TextField()),
                ('difficulty', models.CharField(choices=[('easy','Easy'),('medium','Medium'),('hard','Hard')], default='medium', max_length=10)),
                ('language',   models.CharField(default='python', max_length=30)),
                ('community',  models.CharField(default='c/SolveIt', max_length=80)),
                ('views',      models.PositiveIntegerField(default=0)),
                ('is_premium', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='questions', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(blank=True, related_name='questions', to='codez.tag')),
            ],
            options={'ordering': ['-created_at']},
        ),
        # QuestionVote
        migrations.CreateModel(
            name='QuestionVote',
            fields=[
                ('id',    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1,'Up'),(-1,'Down')])),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='votes', to='codez.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('user', 'question')}},
        ),
        # Answer
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body',        models.TextField()),
                ('code',        models.TextField(blank=True)),
                ('language',    models.CharField(default='python', max_length=30)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_bug',      models.BooleanField(default=False)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('updated_at',  models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='answers', to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='answers', to='codez.question')),
            ],
            options={'ordering': ['-is_accepted', '-created_at']},
        ),
        # AnswerVote
        migrations.CreateModel(
            name='AnswerVote',
            fields=[
                ('id',    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1,'Up'),(-1,'Down')])),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='votes', to='codez.answer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('user', 'answer')}},
        ),
        # Comment
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body',       models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments', to='codez.answer')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['created_at']},
        ),
        # Bookmark
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='bookmarks', to='codez.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='bookmarks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('user', 'question')}, 'ordering': ['-created_at']},
        ),
        # Follow
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('follower',   models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='following', to=settings.AUTH_USER_MODEL)),
                ('following',  models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='followers', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('follower', 'following')}},
        ),
        # Notification
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notif_type', models.CharField(choices=[
                    ('upvote_q','Upvote on Question'),('upvote_a','Upvote on Answer'),
                    ('comment','New Comment'),('follow','New Follower'),
                    ('badge','Badge Earned'),('accepted','Answer Accepted'),
                    ('weekly_rank','Weekly Rank Update')], default='upvote_a', max_length=20)),
                ('message',    models.CharField(max_length=300)),
                ('is_read',    models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answer',   models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='codez.answer')),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='codez.question')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('sender',    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sent_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
