from django.db.models import Q, Sum, Max
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from .models import Product, Member

from utils.pagination_utils import (
  FilterPagination
)

from .models import Product
from .serializers import (
  ProductSerializer,
  ProductSerializerDetail
)

# from rest_framework.permissions import IsAuthenticated
from authentication.custom_permissions import IsAuthenticated

import uuid
from django.conf import settings


class ProductList(APIView):
    permission_classes = []
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        resultset = FilterPagination.get_pagination_data(
            request,
            Product,
            ProductSerializer,
            queries=None,
            order_by_array=('-id',),
            enable_search_inverse=True,  # Active la recherche inverse
            search_inverse_field='title'  # Champ sur lequel chercher (par défaut 'title')
        )
        return Response(resultset)


class ProductDetail(APIView):
  def get_object(self, pk=None, user=None):
    try:
      if pk is not None:
          return Product.objects.get(pk=pk)
      else:
          raise Http404
        
    except Product.DoesNotExist:
      raise Http404


  def get(self, request, pk=None, format=None):
    if pk is not None:
        item = self.get_object(pk=pk)
    else:
        item = self.get_object(user=request.user)
            
            
    serializer = ProductSerializerDetail(item)
    return Response(serializer.data, status=status.HTTP_200_OK)

  def put(self, request, pk, format=None):
    item = self.get_object(pk)
    serializer = ProductSerializer(item, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    item = self.get_object(pk)
    item.delete()
    return Response(status=status.HTTP_200_OK)


# class ProductCreate(APIView):
#     permission_classes = []


#     def post(self, request):
#         author_id = request.user.id
#         print(f"author_id {author_id}")
#         if not author_id:
#             return Response({"error": "L'auteur est requis."}, status=status.HTTP_400_BAD_REQUEST)
#         author = get_object_or_404(Member, id=author_id)

#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=author)  
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductCreateT(APIView):
    """Vue pour créer un produit avec upload d'images"""
    
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def validate_image(self, image_file):
        """Valide le fichier image"""
        # Vérifier l'extension
        ext = image_file.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Extension non autorisée. Utilisez: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Vérifier la taille
        if image_file.size > self.MAX_FILE_SIZE:
            return False, f"Fichier trop volumineux. Taille max: 5MB"
        
        return True, None
    
    def upload_images(self, images_data):
        """Upload les images vers Supabase et retourne les URLs"""
        image_urls = []
        errors = []
        
        for idx, image_file in enumerate(images_data):
            # Validation
            is_valid, error_msg = self.validate_image(image_file)
            if not is_valid:
                errors.append(f"Image {idx + 1}: {error_msg}")
                continue
            
            try:
                # Générer un nom de fichier unique
                ext = image_file.name.split('.')[-1].lower()
                filename = f"products/{uuid.uuid4()}.{ext}"
                
                # Upload vers Supabase
                settings.SUPABASE.storage.from_("product_images").upload(
                    filename, 
                    image_file.read(),
                    file_options={"content-type": image_file.content_type}
                )
                
                # Récupérer l'URL publique
                image_url = settings.SUPABASE.storage.from_("product_images").get_public_url(filename)
                image_urls.append(image_url)
                
            except Exception as e:
                error_msg = f"Image {idx + 1} ({image_file.name}): Échec de l'upload - {str(e)}"
                errors.append(error_msg)
                print(f"[ERROR] {error_msg}")
                continue
        
        return image_urls, errors
    
    def post(self, request):
        """Crée un nouveau produit avec images"""
        author_id = request.user.id
        
        if not author_id:
            return Response(
                {"error": "Authentification requise."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Récupérer l'auteur
        author = get_object_or_404(Member, id=author_id)
        
        # Récupérer les images
        images_data = request.FILES.getlist("images")
        print(f"[INFO] {len(images_data)} image(s) reçue(s)")
        
        # Upload des images
        image_urls = []
        upload_errors = []
        
        if images_data:
            image_urls, upload_errors = self.upload_images(images_data)
            
            # Si aucune image n'a été uploadée avec succès
            if not image_urls and images_data:
                return Response(
                    {
                        "error": "Aucune image n'a pu être uploadée.",
                        "details": upload_errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Préparer les données pour le serializer
        # Utiliser dict() au lieu de copy() pour éviter les problèmes avec les fichiers
        data = {key: value for key, value in request.data.items()}
        if image_urls:
            data["images"] = image_urls
        
        # Créer le produit
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save(author=author)
            
            # Inclure les warnings d'upload si présents
            response_data = serializer.data
            if upload_errors:
                response_data["warnings"] = upload_errors
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class ProductCreate(APIView):
    """Vue pour créer un produit avec upload d'images"""
    
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def validate_image(self, image_file):
        """Valide le fichier image"""
        # Vérifier l'extension
        ext = image_file.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Extension non autorisée. Utilisez: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Vérifier la taille
        if image_file.size > self.MAX_FILE_SIZE:
            return False, f"Fichier trop volumineux. Taille max: 5MB"
        
        return True, None
    
    def upload_images(self, images_data):
        """Upload les images vers Supabase et retourne les URLs"""
        image_urls = []
        errors = []
        
        for idx, image_file in enumerate(images_data):
            # Validation
            is_valid, error_msg = self.validate_image(image_file)
            if not is_valid:
                errors.append(f"Image {idx + 1}: {error_msg}")
                continue
            
            try:
                # Générer un nom de fichier unique
                ext = image_file.name.split('.')[-1].lower()
                filename = f"products/{uuid.uuid4()}.{ext}"
                
                # Upload vers Supabase
                settings.SUPABASE.storage.from_("product_images").upload(
                    filename, 
                    image_file.read(),
                    file_options={"content-type": image_file.content_type}
                )
                
                # Récupérer l'URL publique
                image_url = settings.SUPABASE.storage.from_("product_images").get_public_url(filename)
                image_urls.append(image_url)
                
            except Exception as e:
                error_msg = f"Image {idx + 1} ({image_file.name}): Échec de l'upload - {str(e)}"
                errors.append(error_msg)
                print(f"[ERROR] {error_msg}")
                continue
        
        return image_urls, errors
    
    def post(self, request):
        """Crée un nouveau produit avec images"""
        author_id = request.user.id
        
        if not author_id:
            return Response(
                {"error": "Authentification requise."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Récupérer l'auteur
        author = get_object_or_404(Member, id=author_id)
        
        # Récupérer les images
        images_data = request.FILES.getlist("images")
        print(f"[INFO] {len(images_data)} image(s) reçue(s)")
        
        # Upload des images
        image_urls = []
        upload_errors = []
        
        if images_data:
            image_urls, upload_errors = self.upload_images(images_data)
            
            # Si aucune image n'a été uploadée avec succès
            if not image_urls and images_data:
                return Response(
                    {
                        "error": "Aucune image n'a pu être uploadée.",
                        "details": upload_errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Préparer les données pour le serializer
        # Utiliser dict() au lieu de copy() pour éviter les problèmes avec les fichiers
        data = {key: value for key, value in request.data.items()}
        if image_urls:
            data["images"] = image_urls
        
        # Créer le produit
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save(author=author)
            
            # Inclure les warnings d'upload si présents
            response_data = serializer.data
            if upload_errors:
                response_data["warnings"] = upload_errors
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

class ToggleLikeProductView(APIView):
    """
    Permet à un membre de liker ou déliker un produit.
    """
    def post(self, request, product_id):
        member_id = request.user.id
        if not member_id:
            return Response({"error": "Member ID requis."}, status=status.HTTP_400_BAD_REQUEST)

        member = get_object_or_404(Member, id=member_id)
        product = get_object_or_404(Product, id=product_id)

        if member in product.likes.all():
            product.likes.remove(member)
            action = "removed"
        else:
            product.likes.add(member)
            action = "added"

        return Response({
            "product_id": product.id,
            "total_likes": product.likes.count(),
            "action": action
        }, status=status.HTTP_200_OK)