from rest_framework import serializers
from .models import Preference, Member



from rest_framework import serializers
from .models import Member, Preference


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ['id', 'name']


class MemberSerializer(serializers.ModelSerializer):

    preferences = PreferenceSerializer(many=True, read_only=True)

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
            'preferences',
            'updated_at',
            'created_at',
        )
        read_only_fields = (
            'id',
            'login_date',
            'updated_at',
            'created_at',
        )



class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ['id', 'name']


class UserPreferenceSerializer(serializers.Serializer):
    preferences = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_preferences(self, value):
        # Vérifie que toutes les préférences existent
        existing_ids = list(Preference.objects.values_list('id', flat=True))
        for v in value:
            if v not in existing_ids:
                raise serializers.ValidationError(f"La préférence avec l'id {v} n'existe pas.")
        return value
