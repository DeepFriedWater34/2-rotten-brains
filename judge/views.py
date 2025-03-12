from django.shortcuts import render
from django.db.models import Count, Q
from rest_framework import viewsets
from .models import Problem, Submission, User
from .serializers import SubmissionSerializer

# Leaderboard View
def leaderboard(request):
    users = User.objects.annotate(
        solved=Count('submission', filter=Q(submission__status='accepted'))
    ).order_by('-solved')
    return render(request, 'leaderboard.html', {'users': users})

# API for Submissions
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
