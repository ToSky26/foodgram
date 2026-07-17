from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import User


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
