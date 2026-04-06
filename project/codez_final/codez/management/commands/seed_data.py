"""
codez/management/commands/seed_data.py

Populates the database with sample data so you can see the app working
immediately after setup. Run with:

    python manage.py seed_data

Options:
    --users    N   Number of extra users to create (default 10)
    --questions N  Number of questions to create  (default 30)
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from codez.models import (
    UserProfile, Tag, Question, Answer, QuestionVote, AnswerVote,
    Bookmark, Follow, Notification, LearningPath, LearningStep,
    DailyChallenge,
)
from codez.signals import _seed_badges


# ── Sample content pools ───────────────────────────────────────────────────────
TAGS = [
    'loops', 'recursion', 'sorting', 'arrays', 'strings', 'dict',
    'oop', 'regex', 'files', 'exceptions', 'classes', 'generators',
    'decorators', 'async', 'api', 'sql', 'html', 'css', 'dom',
]

LANGUAGES = ['python', 'javascript', 'java', 'cpp', 'html']
DIFFICULTIES = ['easy', 'medium', 'hard']
COMMUNITIES = ['c/SolveIt', 'c/Debug', 'c/Discuss', 'c/MCQ']

QUESTION_TITLES = [
    "How do I reverse a string in Python without slicing?",
    "Why does my recursive Fibonacci blow the stack?",
    "Explain list comprehensions with a real example",
    "What is the difference between == and 'is' in Python?",
    "How to sort a list of dicts by a nested key?",
    "JavaScript: var vs let vs const — which to use?",
    "Explain closures in JavaScript with a code example",
    "How does async/await differ from Promise chaining?",
    "Java: When should I use an interface vs abstract class?",
    "C++: What is RAII and why does it matter?",
    "How do I avoid SQL injection in raw queries?",
    "What is Big-O and why should I care about it?",
    "How to flatten a deeply nested list in Python?",
    "Explain the difference between stack and heap memory",
    "How do I handle circular imports in Python?",
    "What is memoisation and how do I implement it?",
    "How does garbage collection work in Python vs Java?",
    "Explain the event loop in Node.js",
    "How to implement a binary search in any language?",
    "What is the difference between TCP and UDP?",
    "Explain Python generators vs iterators",
    "How does Django's ORM translate to SQL?",
    "What is a deadlock and how do I prevent it?",
    "How do CSS flexbox and grid differ?",
    "What is REST and what makes an API truly RESTful?",
    "Explain Python's GIL in simple terms",
    "How to design a rate limiter from scratch?",
    "What is currying and partial application?",
    "How do I write a thread-safe singleton in Java?",
    "Explain the CAP theorem with a real-world analogy",
]

ANSWER_BODIES = [
    "Great question! The key insight here is that Python treats strings as immutable sequences, so you need to think carefully about how you build a new one.",
    "The issue is that your base case isn't returning early enough. Remember: every recursive function needs a clearly-defined stopping condition.",
    "Think of it this way: a list comprehension is just a `for` loop that hands you the result immediately, written inside square brackets.",
    "Excellent point to clarify — `==` checks *value equality* while `is` checks *identity* (i.e., whether two variables point to the same object in memory).",
    "You can use `sorted()` with a `lambda` as the `key` argument. The lambda should extract the nested value you want to compare on.",
]

LEARNING_PATH_DATA = [
    {
        'title': 'Python Fundamentals',
        'description': 'Master the basics of Python from variables to OOP.',
        'language': 'python', 'level': 'beginner',
    },
    {
        'title': 'Intermediate Python',
        'description': 'Decorators, generators, context managers and more.',
        'language': 'python', 'level': 'intermediate',
    },
    {
        'title': 'JavaScript Essentials',
        'description': 'Closures, the event loop, promises and async/await.',
        'language': 'javascript', 'level': 'beginner',
    },
    {
        'title': 'Data Structures & Algorithms',
        'description': 'Arrays, linked lists, trees, graphs and Big-O analysis.',
        'language': 'python', 'level': 'intermediate',
    },
    {
        'title': 'Java OOP Mastery',
        'description': 'Classes, interfaces, generics and design patterns.',
        'language': 'java', 'level': 'intermediate',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample data for development.'

    def add_arguments(self, parser):
        parser.add_argument('--users',     type=int, default=10, help='Number of users to create')
        parser.add_argument('--questions', type=int, default=30, help='Number of questions to create')

    # ── Main entry ─────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🌱  Seeding CodeZ database…'))

        _seed_badges()
        self.stdout.write('  ✓ Badges seeded')

        tags = self._create_tags()
        self.stdout.write(f'  ✓ {len(tags)} tags ready')

        users = self._create_users(options['users'])
        self.stdout.write(f'  ✓ {len(users)} users created')

        questions = self._create_questions(users, tags, options['questions'])
        self.stdout.write(f'  ✓ {len(questions)} questions created')

        self._create_answers(users, questions)
        self.stdout.write('  ✓ Answers & votes added')

        self._create_follows(users)
        self.stdout.write('  ✓ Follow relationships added')

        self._create_learning_paths(questions)
        self.stdout.write('  ✓ Learning paths created')

        self._create_daily_challenge(questions)
        self.stdout.write("  ✓ Today's daily challenge set")

        self.stdout.write(self.style.SUCCESS('\n✅  Database seeded successfully!\n'))
        self.stdout.write('  Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('  App:   http://127.0.0.1:8000/\n')

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _create_tags(self):
        tags = []
        for name in TAGS:
            tag, _ = Tag.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            tags.append(tag)
        return tags

    def _create_users(self, count):
        users = []
        for i in range(1, count + 1):
            username = f'coder{i}'
            if User.objects.filter(username=username).exists():
                users.append(User.objects.get(username=username))
                continue
            user = User.objects.create_user(
                username=username,
                email=f'coder{i}@example.com',
                password='password123',
                first_name=random.choice(['Alex', 'Jordan', 'Sam', 'Morgan', 'Taylor', 'Riley']),
                last_name=f'Dev{i}',
            )
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'avatar_seed':  username,
                    'bio':          f'I love solving coding problems! Level {i} coder.',
                    'default_lang': random.choice(LANGUAGES),
                    'points':       random.randint(0, 1500),
                    'xp':           random.randint(0, 500),
                    'level':        random.randint(1, 10),
                    'streak_days':  random.randint(0, 45),
                    'last_active':  timezone.now().date(),
                    'theme':        random.choice(['light', 'dark']),
                }
            )
            users.append(user)
        return users

    def _create_questions(self, users, tags, count):
        questions = []
        titles = (QUESTION_TITLES * ((count // len(QUESTION_TITLES)) + 1))[:count]
        for i, title in enumerate(titles):
            q = Question.objects.create(
                title=title,
                body=(
                    f"Here's my scenario:\n\n"
                    f"I've been working on this for a while and I'm stuck. "
                    f"Here's what I've tried so far:\n\n"
                    f"```\n# attempt {i + 1}\nresult = None\nfor item in data:\n    result = item\n```\n\n"
                    f"Any guidance would be appreciated!"
                ),
                author=random.choice(users),
                difficulty=random.choice(DIFFICULTIES),
                language=random.choice(LANGUAGES),
                community=random.choice(COMMUNITIES),
                views=random.randint(0, 800),
            )
            # Attach 1–3 random tags
            for tag in random.sample(tags, k=random.randint(1, 3)):
                q.tags.add(tag)
            questions.append(q)
        return questions

    def _create_answers(self, users, questions):
        for question in questions:
            # 0–4 answers per question
            answer_authors = random.sample(users, k=min(random.randint(0, 4), len(users)))
            for j, author in enumerate(answer_authors):
                answer = Answer.objects.create(
                    question=question,
                    author=author,
                    body=random.choice(ANSWER_BODIES),
                    code=(
                        f"# Solution approach {j + 1}\n"
                        f"def solve(data):\n"
                        f"    # TODO: implement\n"
                        f"    return data\n"
                    ),
                    language=question.language,
                    is_accepted=(j == 0 and random.random() > 0.6),
                )
                # Add votes to the answer
                voters = random.sample(users, k=random.randint(0, min(5, len(users))))
                for voter in voters:
                    if voter != author:
                        AnswerVote.objects.get_or_create(
                            user=voter, answer=answer,
                            defaults={'value': random.choice([1, 1, 1, -1])},
                        )
            # Add votes to the question
            q_voters = random.sample(users, k=random.randint(0, min(8, len(users))))
            for voter in q_voters:
                if voter != question.author:
                    QuestionVote.objects.get_or_create(
                        user=voter, question=question,
                        defaults={'value': random.choice([1, 1, 1, -1])},
                    )

    def _create_follows(self, users):
        for user in users:
            targets = random.sample([u for u in users if u != user], k=random.randint(1, min(4, len(users) - 1)))
            for target in targets:
                Follow.objects.get_or_create(follower=user, following=target)

    def _create_learning_paths(self, questions):
        for i, data in enumerate(LEARNING_PATH_DATA):
            path, _ = LearningPath.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'language':    data['language'],
                    'level':       data['level'],
                    'order':       i,
                }
            )
            # Link 3–5 questions as steps
            lang_qs = [q for q in questions if q.language == data['language']]
            step_qs = random.sample(lang_qs or questions, k=min(5, len(lang_qs or questions)))
            for order, q in enumerate(step_qs):
                LearningStep.objects.get_or_create(path=path, question=q, defaults={'order': order})

    def _create_daily_challenge(self, questions):
        today = timezone.now().date()
        if not DailyChallenge.objects.filter(date=today).exists():
            DailyChallenge.objects.create(
                date=today,
                question=random.choice(questions),
                bonus_points=random.choice([20, 25, 30]),
            )
