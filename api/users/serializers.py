"""
    User serializer classes
"""
from django.contrib.auth.models import Group
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import User
from .subscription import subscription_service


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    """
    Class to allow related creation if it does not exist
    """

    def to_internal_value(self, data):
        params = {self.slug_field: data}
        obj, _ = self.get_queryset().get_or_create(**params)
        return obj


class UserSerializer(serializers.ModelSerializer):
    """
    User base serializer
    """

    class Meta:  # pylint: disable=C0115,R0903
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class UserDetailedSerializer(UserSerializer):
    """
    User serializer with full detail
    """

    subscription = serializers.CharField(read_only=True)
    groups = serializers.SlugRelatedField(
        read_only=True, many=True, slug_field="name"
    )

    class Meta:  # pylint: disable=C0115,R0903
        model = User
        fields = UserSerializer.Meta.fields + (
            "email",
            "groups",
            "subscription",
            "created",
            "updated",
            "password",
        )


class ValidateEmailSerializerMixin:  # pylint: disable=R0903
    """
    Mixin to validate if an email exists and it doesnt belong to the user
    """

    def validate_email(self, value):
        """Validate email doesnt exist"""
        user = self.context["request"].user
        qset = User.objects.exclude(pk=user.pk).filter(email=value)

        if qset.exists():
            raise serializers.ValidationError(
                {"email": "E-mail already exists."}
            )
        return value


class StaffUserUpdateSerializer(ValidateEmailSerializerMixin, UserSerializer):
    """
    Serializer to update users by staff
    """

    groups = CreatableSlugRelatedField(
        queryset=Group.objects, many=True, slug_field="name"
    )

    class Meta:  # pylint: disable=C0115,R0903
        model = User
        fields = UserSerializer.Meta.fields + (
            "email",
            "groups",
            "password",
        )


def validate_password_field(value, instance):
    """Validate password with django builtin validation"""
    try:
        password_validation.validate_password(value, instance)
    except ValidationError as ex:
        messages = []
        for detail in ex.error_list:
            if detail.params:
                msg = detail.message % detail.params
            else:
                msg = detail.message
            messages.append(msg)
        raise serializers.ValidationError(" ".join(messages))


class NonStaffUserUpdateSerializer(
    ValidateEmailSerializerMixin, UserSerializer
):
    """
    Serializer to update users by non staff
    """

    old_password = serializers.CharField()

    def validate_password(self, value):
        """Validate with django built-in"""
        validate_password_field(value, self.instance)
        return value

    def update(self, instance, validated_data, *args, **kwargs):
        """Update non staff user"""
        old_password = validated_data.pop("old_password", "")
        if not old_password:
            raise serializers.ValidationError("Previous password is required")

        user = self.context["request"].user

        if self.instance.id != user.id:
            raise serializers.ValidationError("Invalid user id")

        if not self.instance.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect")
        return super().update(instance, validated_data, *args, **kwargs)

    class Meta:  # pylint: disable=C0115,R0903
        model = User
        fields = UserSerializer.Meta.fields + (
            "email",
            "password",
            "old_password",
        )


class UserCreateSerializer(UserDetailedSerializer):
    """
    Serializer to create user
    """

    password = serializers.CharField()
    repeat_password = serializers.CharField(write_only=True)
    groups = CreatableSlugRelatedField(
        queryset=Group.objects, many=True, slug_field="name"
    )

    def validate_password(self, value):
        """Validate with django builtin"""
        validate_password_field(value, self.instance)
        return value

    def validate_repeat_password(self, value):
        """Validate password confirmation"""
        if value != self.initial_data["password"]:
            raise serializers.ValidationError("Password doesn't match")

    def create(self, validated_data, *args, **kwargs):
        """User creation function"""
        validated_data.pop("repeat_password")

        obj = super().create(validated_data, *args, **kwargs)
        result = subscription_service.fetch_subscription(obj.id)

        obj.subscription = result["subscription"]
        obj.save()

        return obj

    class Meta:  # pylint: disable=C0115,R0903
        model = User
        fields = UserDetailedSerializer.Meta.fields + (
            "password",
            "repeat_password",
        )
