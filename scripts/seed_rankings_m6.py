#!/usr/bin/env python3
"""
Seed users, ratings, and organizations for Milestone 6 (Screens 6 & 7).
"""
import os
import sys
from pathlib import Path
from datetime import timedelta

JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from judge.models import Profile, Organization, Contest, ContestParticipation, Rating, Problem, Submission, Language

User = get_user_model()
now = timezone.now()

# 1. Create Organizations (Countries/Teams)
orgs_data = [
    ('Canada', 'CAN'),
    ('United States', 'USA'),
    ('China', 'CHN'),
    ('Singapore', 'SGP'),
    ('Australia', 'AUS'),
]
org_objs = {}
for name, short_name in orgs_data:
    org, _ = Organization.objects.get_or_create(
        slug=short_name.lower(),
        defaults={'name': name, 'short_name': short_name, 'is_open': True}
    )
    org_objs[name] = org

# 2. Seed Top Competitive Programmers matching mockup docs/6.png & docs/7.png
users_data = [
    {
        'username': 'ecnerwala',
        'email': 'ecnerwala@vcoder.judge',
        'rating': 3421,
        'points': 8920.0,
        'problem_count': 523,
        'performance_points': 3421.0,
        'org': 'Canada',
        'about': 'Competitive programmer. Codeforces #1, IOI Gold medalist.',
    },
    {
        'username': 'tourist',
        'email': 'tourist@vcoder.judge',
        'rating': 3287,
        'points': 8650.0,
        'problem_count': 487,
        'performance_points': 3287.0,
        'org': 'Canada',
        'about': 'I like algorithms, mathematics, and good problems.',
    },
    {
        'username': 'qwqaqa',
        'email': 'qwqaqa@vcoder.judge',
        'rating': 3176,
        'points': 7840.0,
        'problem_count': 431,
        'performance_points': 3176.0,
        'org': 'United States',
        'about': 'Algorithms and competitive programming enthusiast.',
    },
    {
        'username': 'matthew99',
        'email': 'matthew99@vcoder.judge',
        'rating': 3041,
        'points': 7210.0,
        'problem_count': 412,
        'performance_points': 3041.0,
        'org': 'United States',
        'about': 'USACO Platinum, IOI silver.',
    },
    {
        'username': 'BlueBook',
        'email': 'bluebook@vcoder.judge',
        'rating': 2993,
        'points': 6940.0,
        'problem_count': 398,
        'performance_points': 2993.0,
        'org': 'Canada',
        'about': 'Canadian Computing Olympiad finalist.',
    },
    {
        'username': 'admin',
        'email': 'admin@vcoder.judge',
        'rating': 2341,
        'points': 6500.0,
        'problem_count': 421,
        'performance_points': 2341.0,
        'org': 'Canada',
        'about': 'I like algorithms, mathematics, and good problems.',
    },
]

# Ensure at least 1 contest for rating entries
contest, _ = Contest.objects.get_or_create(
    key='weekly1',
    defaults={
        'name': 'Weekly Practice Round #1',
        'start_time': now - timedelta(days=7),
        'end_time': now - timedelta(days=7, hours=-2),
        'is_rated': True,
        'is_visible': True,
    }
)

for ud in users_data:
    u, created = User.objects.get_or_create(
        username=ud['username'],
        defaults={'email': ud['email']}
    )
    if created:
        u.set_password('Vcoder123@@')
        u.save()

    profile, _ = Profile.objects.get_or_create(user=u)
    profile.rating = ud['rating']
    profile.points = ud['points']
    profile.problem_count = ud['problem_count']
    profile.performance_points = ud['performance_points']
    profile.about = ud['about']
    profile.is_unlisted = False
    profile.save()

    # Link to organization
    org = org_objs.get(ud['org'])
    if org:
        profile.organizations.set([org])

    part, _ = ContestParticipation.objects.get_or_create(
        contest=contest,
        user=profile,
        defaults={'real_start': now - timedelta(days=7), 'cumtime': 120, 'score': ud['points']}
    )

    Rating.objects.get_or_create(
        user=profile,
        contest=contest,
        defaults={
            'rating': ud['rating'],
            'rank': 1,
            'participation': part,
            'mean': ud['rating'],
            'performance': ud['rating'],
            'last_rated': now - timedelta(days=7),
        }
    )

print("Rankings and User Profiles successfully seeded!")
