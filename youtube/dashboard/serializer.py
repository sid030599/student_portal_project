from rest_framework import serializers
from dashboard.models import Homework

class Homework_masterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Homework
        fields = '__all__'