from rest_framework import serializers
from member.models import Member

class LoginSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'email',
      'password',
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
