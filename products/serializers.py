from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Product
    fields = (
      'id', 
      'title', 
      'image', 
      'type', 
      'description', 
      'author', 
      'likes', 
      'created_at', 
      'updated_at'
    )
    read_only_fields = (
      'likes', 
      'created_at', 
      'updated_at'
    )