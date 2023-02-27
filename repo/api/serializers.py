from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class AuthTokenSerializer(serializers.Serializer):
    """AuthToken Serializer."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(request=self.context["request"], **attrs)
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        return {"user": user}


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer to register new users."""

    terms = serializers.BooleanField()

    class Meta:
        """Meta class for Register Serializer."""

        model = User
        exclude = ["created_at", "updated_at"]

    def validate(self, attrs):
        errors = []

        validate_password(attrs["password"])

        if not attrs.get("terms"):
            errors.append("Read and accept our terms and conditions!")
        if User.objects.filter(email=attrs.get("email")):
            errors.append("Email address already in use.")

        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)

    def create(self, validated_data):
        """Create user with the object manager."""
        data = validated_data
        User.objects.create_user(data["email"], data["password"], name=data["name"])

        return data

    def to_representation(self, instance):
        data = {"message": "User created successfully!"}
        return data
