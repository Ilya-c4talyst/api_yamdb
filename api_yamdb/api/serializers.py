from django.core.exceptions import ValidationError
from rest_framework import serializers

from reviews.models import Comment, Review


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='text')
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    
    class Meta:
        fields = "__all__"
        model = Review
    
    def validate(self, data):
        author = self.context['request'].user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(title=title_id, author=author).exists():
            raise ValidationError('Вы уже писали отзыв к этому произведению')
        return data
    
    def validate_score(self, value):
        if 0 > value > 10:
            raise ValidationError('Оценкой может быть число от 1 до 10')
        return value


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        read_only=True, slug_field='name')
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = "__all__"
        model = Comment