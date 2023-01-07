from django.contrib.auth import authenticate
from rest_framework import serializers


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(request=self.context["request"], **attrs)
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        return {"user": user}
