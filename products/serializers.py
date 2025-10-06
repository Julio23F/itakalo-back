from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    total_likes = serializers.IntegerField(source='likes.count', read_only=True)
    images = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True
    )
    mots_cles_recherches = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'images',
            'type',
            'price',
            'category',
            'description',
            'author',
            'author_name',
            'likes',
            'total_likes',
            'adresse',
            'mots_cles_recherches',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'author',
            'author_name',
            'likes',
            'total_likes',
            'created_at',
            'updated_at'
        )
    
    def validate_images(self, value):
        """Valide la liste d'URLs d'images"""
        if value and len(value) > 10:
            raise serializers.ValidationError("Maximum 10 images autorisées")
        return value
    
    def validate_mots_cles_recherches(self, value):
        """Valide la liste de mots-clés"""
        if value and len(value) > 20:
            raise serializers.ValidationError("Maximum 20 mots-clés autorisés")
        
        # Nettoyer et normaliser les mots-clés
        cleaned = []
        for mot in value:
            mot_clean = mot.strip().lower()
            if mot_clean and len(mot_clean) >= 2:
                cleaned.append(mot_clean)
        
        # Supprimer les doublons
        return list(set(cleaned))
    
    def validate_price(self, value):
        """Valide le prix"""
        if value < 0:
            raise serializers.ValidationError("Le prix ne peut pas être négatif")
        return value
    
    def validate(self, data):
        """Validation globale"""
        # Si c'est une vente, le prix doit être > 0
        if data.get('type') == 'SALE' and data.get('price', 0) <= 0:
            raise serializers.ValidationError({
                'price': "Le prix doit être supérieur à 0 pour une vente"
            })
        
        # Si c'est un don, le prix doit être 0
        if data.get('type') == 'DONATION' and data.get('price', 0) != 0:
            data['price'] = 0  # Forcer à 0
        
        return data