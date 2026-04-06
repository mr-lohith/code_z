from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codez', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Feature 1: Learning Paths ─────────────────────────────────────────
        migrations.CreateModel(
            name='LearningPath',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title',       models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('language',    models.CharField(max_length=30, default='python')),
                ('level',       models.CharField(max_length=15, choices=[('beginner','Beginner'),('intermediate','Intermediate'),('pro','Pro')], default='beginner')),
                ('order',       models.PositiveIntegerField(default=0)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['language', 'order']},
        ),
        migrations.CreateModel(
            name='LearningStep',
            fields=[
                ('id',    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('path',     models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='codez.learningpath')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_steps', to='codez.question')),
            ],
            options={'ordering': ['order'], 'unique_together': {('path', 'question')}},
        ),
        migrations.CreateModel(
            name='UserPathProgress',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('user',            models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='path_progress', to=settings.AUTH_USER_MODEL)),
                ('path',            models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='codez.learningpath')),
                ('completed_steps', models.ManyToManyField(blank=True, related_name='completions', to='codez.learningstep')),
            ],
            options={'unique_together': {('user', 'path')}},
        ),

        # ── Feature 2: Daily Challenges ───────────────────────────────────────
        migrations.CreateModel(
            name='DailyChallenge',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date',         models.DateField(unique=True)),
                ('bonus_points', models.PositiveIntegerField(default=20)),
                ('question',     models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_challenges', to='codez.question')),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='DailyChallengeCompletion',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('user',      models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_completions', to=settings.AUTH_USER_MODEL)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completions', to='codez.dailychallenge')),
            ],
            options={'unique_together': {('user', 'challenge')}},
        ),

        # ── Feature 4: Project Forum ──────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectPost',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title',       models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('code',        models.TextField(blank=True)),
                ('language',    models.CharField(max_length=30, default='python')),
                ('repo_url',    models.URLField(blank=True)),
                ('demo_url',    models.URLField(blank=True)),
                ('views',       models.PositiveIntegerField(default=0)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('updated_at',  models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL)),
                ('tags',   models.ManyToManyField(blank=True, related_name='projects', to='codez.tag')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ProjectUpvote',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user',    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to='codez.projectpost')),
            ],
            options={'unique_together': {('user', 'project')}},
        ),
        migrations.CreateModel(
            name='ProjectFeedback',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body',          models.TextField()),
                ('is_bug_report', models.BooleanField(default=False)),
                ('created_at',    models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='codez.projectpost')),
                ('author',  models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_feedbacks', to=settings.AUTH_USER_MODEL)),
                ('upvotes', models.ManyToManyField(blank=True, related_name='upvoted_feedbacks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),

        # ── Feature 5: Doubt Solving ──────────────────────────────────────────
        migrations.CreateModel(
            name='DoubtThread',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title',       models.CharField(max_length=200)),
                ('body',        models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doubt_threads', to='codez.question')),
                ('author',   models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doubt_threads', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='DoubtReply',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body',        models.TextField()),
                ('is_accepted', models.BooleanField(default=False)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('thread',   models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='codez.doubtthread')),
                ('author',   models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doubt_replies', to=settings.AUTH_USER_MODEL)),
                ('upvotes',  models.ManyToManyField(blank=True, related_name='upvoted_doubt_replies', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['created_at']},
        ),
    ]
