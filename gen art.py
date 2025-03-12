#task1:Implement user authentication with different access levels (admin, participant, judge).
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('participant', 'Participant'),
        ('judge', 'Judge'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
#Create a problem submission system with test case evaluation.
class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    test_cases = models.JSONField()  # Store test cases as JSON
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20, choices=[('python', 'Python'), ('cpp', 'C++')])
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])
    execution_time = models.FloatField(null=True)
    memory_used = models.FloatField(null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


