from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from terminal.models import Session
from acls.models import CommandGroup, CommandFilterACL
from common.utils import lazyproperty, get_object_or_none
from common.serializers.fields import ObjectRelatedField, LabeledChoiceField
from orgs.utils import tmp_to_root_org
from orgs.mixins.serializers import BulkOrgResourceModelSerializer
from .base import BaseUserAssetAccountACLSerializerMixin as BaseSerializer

__all__ = ["CommandFilterACLSerializer", "CommandGroupSerializer", "CommandReviewSerializer"]


class CommandGroupSerializer(BulkOrgResourceModelSerializer):
    type = LabeledChoiceField(
        choices=CommandGroup.TypeChoices.choices, default=CommandGroup.TypeChoices.command,
        label=_('Type')
    )

    class Meta:
        model = CommandGroup
        fields = ['id', 'name', 'type', 'content', 'ignore_case', 'comment']


class CommandFilterACLSerializer(BaseSerializer, BulkOrgResourceModelSerializer):
    command_groups = ObjectRelatedField(
        queryset=CommandGroup.objects, many=True, required=False, label=_('Command group')
    )
    command_groups_amount = serializers.IntegerField(
        source='command_groups.count', read_only=True, label=_('Command group amount')
    )

    class Meta(BaseSerializer.Meta):
        model = CommandFilterACL
        fields = BaseSerializer.Meta.fields + ['command_groups', 'command_groups_amount']


class CommandReviewSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=True, allow_null=False)
    cmd_filter_acl_id = serializers.UUIDField(required=True, allow_null=False)
    run_command = serializers.CharField(required=True, allow_null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None
        self.cmd_filter_acl = None

    def validate_session_id(self, pk):
        self.session = self.validate_object(Session, pk)
        return pk

    def validate_cmd_filter_acl_id(self, pk):
        self.cmd_filter_acl = self.validate_object(CommandFilterACL, pk)
        return pk

    @lazyproperty
    def org(self):
        return self.session.org

    @staticmethod
    def validate_object(model, pk):
        with tmp_to_root_org():
            obj = get_object_or_none(model, id=pk)
        if obj:
            return obj
        error = '{} Model object does not exist'.format(model.__name__)
        raise serializers.ValidationError(error)
