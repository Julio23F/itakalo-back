from rest_framework import serializers
from member.models import Member


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


    
class LoginSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'email',
      'password',
      'profile_picture', 
      'is_google_user', 
    )

class RegisterSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'email',
      'type',
      'first_name',
      'last_name',
      'telnumber',
      'password',
      'udid',
      'profile_picture', 
      'is_google_user', 
    )


class RegisterByEmailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'email',
      'type',
      'first_name',
      'last_name',
      'telnumber',
      'birth_date',
      'password',
      'plat_form',
      'udid',
      'profile_picture', 
      'is_google_user', 
    )

class ChangeEmailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'email',
    )

class ChangePasswordSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'email',
      'new_password'
    )

class ForgetPasswordSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'email',
    )
