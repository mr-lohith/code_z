"""
Migration 0003 — fix notif_type max_length

0002_features already creates ProjectFeedback, DoubtThread, and DoubtReply
with all their fields (including upvotes M2M).  This migration only extends
the Notification.notif_type field from max_length=20 to max_length=25 so
the new notification type strings ('project_feedback', 'doubt_upvote',
'daily_reward', 'bug_reward') fit in the column.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codez', '0002_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notif_type',
            field=models.CharField(
                max_length=25,
                choices=[
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
                ],
                default='upvote_a',
            ),
        ),
    ]
