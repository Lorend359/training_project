from rest_framework import serializers

from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    Запрашивает email, ФИО и пароль. Подтверждения пароля нет — это упрощает процесс для пожилых пользователей.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "full_name", "password")

    def create(self, validated_data):
        """
        Метод вызывается при .save(). Использует create_user, чтобы пароль хешировался.
        """
        return CustomUser.objects.create_user(**validated_data)
