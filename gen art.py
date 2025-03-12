from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models import Count, Q
from django.shortcuts import render
import docker
import os
import subprocess
import random
from rest_framework import serializers
from django.contrib import admin
from channels.generic.websocket import AsyncWebsocketConsumer
import json


#  User Authentication with Different Access Levels
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('participant', 'Participant'),
        ('judge', 'Judge'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')


#  Problem Submission System with Test Case Evaluation
class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    test_cases = models.JSONField()  # Store test cases as JSON
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)


class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20, choices=[('python', 'Python'), ('cpp', 'C++')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    execution_time = models.FloatField(null=True, blank=True)
    memory_used = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


#  Real-time Leaderboard
def leaderboard(request):
    users = User.objects.annotate(
        solved=Count('submission', filter=Q(submission__status='accepted'))
    ).order_by('-solved')
    return render(request, 'leaderboard.html', {'users': users})


#  Secure Code Execution Sandbox
LANGUAGE_CONTAINERS = {
    'python': 'python:3.8',
    'cpp': 'gcc:latest',
    'java': 'openjdk:11',
}

def execute_code(code, language):
    client = docker.from_env()
    container_image = LANGUAGE_CONTAINERS.get(language, "python:3.8")

    try:
        container = client.containers.run(
            container_image,
            command=f"python3 -c '{code}'" if language == 'python' else f"g++ -o main.out && ./main.out",
            detach=True,
            auto_remove=True,
            mem_limit="100m",
            cpu_period=50000
        )
        return container.logs()
    except Exception as e:
        return str(e)


#  Plagiarism Detection (MOSS Integration)
def check_plagiarism(submission):
    moss_script_path = "moss.pl"  # Ensure MOSS script is installed
    moss_user_id = "123456789"  # Replace with actual MOSS ID

    file_path = f"temp_code/{submission.user.username}_{submission.problem.id}.txt"
    os.makedirs("temp_code", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(submission.code)

    cmd = f"perl {moss_script_path} -u {moss_user_id} {file_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    return result.stdout  # Moss returns similarity percentage


#  Contest System
class Contest(models.Model):
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField(Problem)
    participants = models.ManyToManyField(User)

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time


#  User Rating System
class UserRating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1500)


#  WebSockets for Real-Time Timer
class TimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"time": "Contest started!"}))


#  Language Containers for Execution
LANGUAGE_CONTAINERS = {
    'python': 'python:3.8',
    'cpp': 'gcc:latest',
    'java': 'openjdk:11',
}


#  Team Collaboration
class Team(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User)


#  API Serializer for Submission
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


#  Admin Panel Registration
admin.site.register(User)
admin.site.register(Problem)
admin.site.register(Submission)
admin.site.register(Contest)


#  Problem Recommendation System
def recommend_problems(user):
    solved_problems = user.submission_set.filter(status='accepted').values_list('problem_id', flat=True)
    return Problem.objects.exclude(id__in=solved_problems).order_by('?')[:5]


#  Achievement Badges
class Badge(models.Model):
    name = models.CharField(max_length=100)
    criteria = models.CharField(max_length=200)


#  Random Test Case Generation
def generate_test_case():
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    return f"{a} {b}", f"{a + b}"


# Submission History View
def submission_history(request):
    submissions = Submission.objects.filter(user=request.user)
    return render(request, 'submission_history.html', {'submissions': submissions})


# Forum System
class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


#  Problem Rating System
class ProblemRating(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()


#  Database Backup & Restore (Commands)
"""
# Backup
python manage.py dumpdata > backup.json

# Restore
python manage.py loaddata backup.json
"""



#  Contest Statistics
def contest_stats(contest):
    submissions = Submission.objects.filter(problem__contest=contest)
    return {"total_submissions": submissions.count()}
