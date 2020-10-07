from rest_framework import serializers
from .models import Category, Question, Answer
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(source='question', queryset=Question.objects.all(), required=False)
    user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), required=False)

    class Meta: 
        model = Answer
        fields = ('answer_id', 'question_id', 'created_timestamp', 'updated_timestamp', 'user_id', 'answer_text')
        # extra_kwargs = {
        #     'question': {'required': False}
        # }
 
    # def update(self, instance, validated_data):
    #     instance.answer_text = validated_data.get('answer_text', instance.answer_text)
    #     instance.updated_timestamp = timezone.now()
    #     instance.save()
    #     return instance    


class QuestionSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)
    answers = AnswerSerializer(many=True, required=False)
    user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), required=False)

    class Meta:
        model = Question
        fields = ['question_id', 'created_timestamp', 'updated_timestamp', 'user_id', 'question_text', 'categories', 'answers']
        # extra_kwargs = {
        #     'categories': {'allow_empty': True}
        # }\

    def create(self, validated_data):
        user_id = validated_data['user_id']
        categories = validated_data.pop('categories', {})
        answers = validated_data.pop('answers', {})
        q = Question.objects.create(**validated_data)
        for v in categories: 
            if Category.objects.filter(category=v['category']):
                category = Category.objects.filter(category=v['category'])[0]
                category.questions.add(q)
            else:
                category = Category.objects.create(category=v['category'])
                category.questions.add(q)
            category.save()
        for v in answers:
            Answer.objects.create(answer_text=v['answer_text'], user_id=user_id, question_id=q.pk)

        return q

    def update(self, instance, validated_data):
        instance.question_text = validated_data.get('question_text', instance.question_text)
        categories = validated_data.pop('categories', {})
        if categories:
            instance.categories.clear()
            instance.save()
            for v in categories: 
                if Category.objects.filter(category=v['category']):
                    category = Category.objects.filter(category=v['category'])[0]
                    category.questions.add(instance)
                else:
                    category = Category.objects.create(category=v['category'])
                    category.questions.add(instance)
            category.save()
            instance.updated_timestamp = timezone.now()
            instance.save()
        return instance



