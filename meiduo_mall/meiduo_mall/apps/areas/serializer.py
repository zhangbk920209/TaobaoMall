from rest_framework import serializers

from areas.models import Area


# 省级地区序列化器
class ProvinceDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ('id', 'name')


# 查询某地区及其子级地区序列化器
class SubAreasDataSerializer(serializers.ModelSerializer):
    sub = ProvinceDataSerializer(label='下级地区', many=True)
    class Meta:
        model = Area
        fields = ('id', 'name', 'sub')