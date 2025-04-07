from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import ReadOnlyOrAdmin
from rest_framework.decorators import action
from rest_framework.response import Response
from roadmap.models import Project, Employee, Task, TaskAssignment
from .serializers import ProjectSerializer, EmployeeSerializer, TaskSerializer, TaskAssignmentSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [ReadOnlyOrAdmin]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [ReadOnlyOrAdmin]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'assigned_employees__user__username', 'deadline','month','year__year']
    search_fields = ['name', 'description', 'project__name', 'assigned_employees__user__username','deadline','month','year__year']
    ordering_fields = ['deadline']
    permission_classes = [ReadOnlyOrAdmin]

    @action(detail=False, methods=['GET'])
    def monthly_tasks(self, request):
        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)

        if not month or not year:
            return Response({"error": "Please provide both 'month' and 'year' parameters"}, status=400)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Invalid month or year format"}, status=400)

        tasks = Task.objects.filter(Q(year__year=year) & Q(month=month))
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TaskAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TaskAssignment.objects.all()
    serializer_class = TaskAssignmentSerializer
    permission_classes = [ReadOnlyOrAdmin]

