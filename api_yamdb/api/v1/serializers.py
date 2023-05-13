from rest_framework import serializers
from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)
    username = serializers.SlugField(read_only=True)
    email = serializers.SlugField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class UserAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        if self.initial_data.get('username') == 'me':
            raise serializers.ValidationError(
                'Ошибка: нельзя использовать данное имя!'
            )
        return data


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if self.initial_data.get('username') == 'me':
            raise serializers.ValidationError(
                'Ошибка: нельзя использовать данное имя!'
            )
        return data


class GetTokenSerializer(serializers.Serializer):
    username = serializers.SlugField(required=True)
    confirmation_code = serializers.SlugField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
