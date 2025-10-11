from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = (
            'id',
            'image',
            'email',
            'type',
            'first_name',
            'last_name',
            'telnumber',

            'profile_picture', 
            'is_google_user',

            'updated_at',
            'created_at'
        )
        read_only_fields = (
            'id',
            'login_date',
            'updated_at',
            'created_at',
        )
