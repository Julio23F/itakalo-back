from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
  followers = serializers.SerializerMethodField()
  
  class Meta:
    model = Member
    fields = (
      'id',
      # 'image',
      'email',
      'type',
      'first_name',
      'last_name',
      'telnumber',
      # 'password',
      # 'active_notification',
      # 'udid',
      # 'login_date',
      # 'is_valid_email',
      'updated_at',
      'created_at',
      'followers'
    )
    read_only_fields = (
      'id',
      'login_date',
      'updated_at',
      'created_at',
    )
    
  def get_followers(self, obj):
        followers = obj.followers.all()
        return [{
          'id': f.id, 
          'email': f.email, 
          'first_name': f.first_name, 
          'last_name': f.last_name, 
          'telnumber': f.telnumber
        } for f in followers]
    
    
    
      
class FollowingMemberSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Member
    fields = (
      'id',
      'email',
      'type',
      'first_name',
      'last_name',
      'telnumber',
      'updated_at',
      'created_at',
    )
    read_only_fields = (
      'id',
      'login_date',
      'updated_at',
      'created_at',
    )