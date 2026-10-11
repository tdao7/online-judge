# -*- coding: utf-8 -*-
"""
VCoderLog Assessment Bridge API for DMOJ Arena.
Endpoints:
1. POST /api/v2/vcoderlog/candidate/register
   Creates or updates an Arena student account and registers them to the placement contest.
2. GET /api/v2/vcoderlog/candidate/<username>/results
   Retrieves candidate's live contest scores, verdicts, and submission details.
"""

import json
from datetime import timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from judge.models import Profile, Contest, ContestProblem, ContestParticipation, Submission, Problem

@csrf_exempt
def register_candidate(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed. Use POST.'}, status=405)
    
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
        else:
            payload = request.POST.dict()
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Invalid request payload: {str(e)}'}, status=400)
    
    username = payload.get('username', '').strip().lower()
    password = payload.get('password', '').strip()
    display_name = payload.get('display_name', '').strip()
    email = payload.get('email', '').strip()
    contest_key = payload.get('contest_key', 'chuyentin90').strip()
    
    if not username:
        return JsonResponse({'success': False, 'error': 'username is required.'}, status=400)
    if not password:
        return JsonResponse({'success': False, 'error': 'password is required.'}, status=400)
        
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email or f"{username}@vcoderlog.edu.vn"}
        )
        user.set_password(password)
        if display_name:
            user.first_name = display_name[:30]
        if email:
            user.email = email
        user.save()
        
        profile, p_created = Profile.objects.get_or_create(
            user=user,
            defaults={'display_rank': 'user', 'timezone': 'Asia/Ho_Chi_Minh'}
        )
        profile.display_name = display_name or username
        profile.save()
        
        contest = Contest.objects.filter(key=contest_key).first()
        contest_registered = False
        if contest:
            part, _ = ContestParticipation.objects.get_or_create(
                contest=contest,
                user=profile,
                defaults={
                    'real_start': timezone.now(),
                    'cumtime': 0,
                }
            )
            contest_registered = True
            
        return JsonResponse({
            'success': True,
            'message': 'Candidate account provisioned successfully.',
            'created': created,
            'username': username,
            'display_name': profile.display_name,
            'email': user.email,
            'contest_key': contest_key,
            'contest_name': contest.name if contest else '',
            'contest_registered': contest_registered,
            'contest_url': f"/contest/{contest_key}" if contest else '',
            'login_url': "/login/"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Failed to register candidate: {str(e)}'}, status=500)


def get_candidate_results(request, username):
    contest_key = request.GET.get('contest_key', 'chuyentin90').strip()
    
    try:
        profile = Profile.objects.get(user__username=username.strip().lower())
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': f"User '{username}' does not exist on Arena."}, status=404)
        
    contest = Contest.objects.filter(key=contest_key).first()
    if not contest:
        return JsonResponse({'success': False, 'error': f"Contest '{contest_key}' not found."}, status=404)
        
    contest_problems = ContestProblem.objects.filter(contest=contest).select_related('problem').order_by('order')
    
    problem_results = {}
    total_earned_score = 0.0
    total_max_score = 0.0
    
    for cp in contest_problems:
        prob = cp.problem
        max_pts = float(cp.points or prob.points)
        total_max_score += max_pts
        
        subs = Submission.objects.filter(user=profile, problem=prob).order_by('-case_points', '-id')
        sub_count = subs.count()
        best_sub = subs.first()
        
        if best_sub:
            earned = float(best_sub.case_points if best_sub.case_points is not None else 0.0)
            verdict = best_sub.result
            sub_id = best_sub.id
            sub_time = best_sub.time
            sub_mem = best_sub.memory
            sub_lang = best_sub.language.key if best_sub.language else ''
            sub_date = best_sub.date.isoformat() if best_sub.date else ''
        else:
            earned = 0.0
            verdict = 'UNSUBMITTED'
            sub_id = None
            sub_time = None
            sub_mem = None
            sub_lang = None
            sub_date = None
            
        total_earned_score += earned
        
        problem_results[prob.code] = {
            'order': cp.order,
            'code': prob.code,
            'name': prob.name,
            'score': round(earned, 2),
            'max_score': max_pts,
            'verdict': verdict,
            'submissions_count': sub_count,
            'best_submission_id': sub_id,
            'time': sub_time,
            'memory': sub_mem,
            'language': sub_lang,
            'submitted_at': sub_date,
        }
        
    return JsonResponse({
        'success': True,
        'username': username,
        'display_name': profile.display_name,
        'contest_key': contest.key,
        'contest_name': contest.name,
        'total_coding_score': round(total_earned_score, 2),
        'max_coding_score': round(total_max_score, 2),
        'problems': problem_results,
    })
