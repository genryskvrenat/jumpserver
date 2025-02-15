# -*- coding: utf-8 -*-
#
from rest_framework import status, viewsets
from rest_framework.response import Response

from orgs.mixins.api import OrgBulkModelViewSet
from common.const.choices import Trigger
from accounts import serializers
from accounts.tasks import execute_account_backup_plan
from accounts.models import (
    AccountBackupAutomation, AccountBackupExecution
)

__all__ = [
    'AccountBackupPlanViewSet', 'AccountBackupPlanExecutionViewSet'
]


class AccountBackupPlanViewSet(OrgBulkModelViewSet):
    model = AccountBackupAutomation
    filter_fields = ('name',)
    search_fields = filter_fields
    ordering_fields = ('name',)
    ordering = ('name',)
    serializer_class = serializers.AccountBackupSerializer


class AccountBackupPlanExecutionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AccountBackupPlanExecutionSerializer
    search_fields = ('trigger',)
    filterset_fields = ('trigger', 'plan_id')
    http_method_names = ['get', 'post', 'options']

    def get_queryset(self):
        queryset = AccountBackupExecution.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pid = serializer.data.get('plan')
        task = execute_account_backup_plan.delay(pid=pid, trigger=Trigger.manual)
        return Response({'task': task.id}, status=status.HTTP_201_CREATED)
