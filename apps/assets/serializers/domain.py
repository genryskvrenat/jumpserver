# -*- coding: utf-8 -*-
#
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from common.serializers.fields import ObjectRelatedField
from orgs.mixins.serializers import BulkOrgResourceModelSerializer
from .gateway import GatewayWithAccountSecretSerializer
from ..models import Domain, Asset

__all__ = ['DomainSerializer', 'DomainWithGatewaySerializer']


class DomainSerializer(BulkOrgResourceModelSerializer):
    gateways = ObjectRelatedField(
        many=True, required=False, queryset=Asset.objects, label=_('Gateway')
    )
    assets = ObjectRelatedField(
        many=True, required=False, queryset=Asset.objects, label=_('Asset')
    )

    class Meta:
        model = Domain
        fields_mini = ['id', 'name']
        fields_small = fields_mini + ['comment']
        fields_m2m = ['assets', 'gateways']
        read_only_fields = ['date_created']
        fields = fields_small + fields_m2m + read_only_fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        assets = data['assets']
        gateway_ids = [str(i['id']) for i in data['gateways']]
        data['assets'] = [i for i in assets if str(i['id']) not in gateway_ids]
        return data


class DomainWithGatewaySerializer(serializers.ModelSerializer):
    gateways = GatewayWithAccountSecretSerializer(many=True, read_only=True)

    class Meta:
        model = Domain
        fields = '__all__'
