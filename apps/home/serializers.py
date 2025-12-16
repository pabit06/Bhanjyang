from rest_framework import serializers
from .models import Statistic, Testimonial

class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = ['id', 'title', 'value', 'description', 'icon', 'color', 'order']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'position', 'company', 'content', 'rating', 'photo', 'language', 'order']
