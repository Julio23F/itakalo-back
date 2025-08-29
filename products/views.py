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
)

# from rest_framework.permissions import IsAuthenticated
from authentication.custom_permissions import IsAuthenticated

# from utils.email_utils import send_email_Product_password

class ProductList(APIView):
  permission_classes = []
  # permission_classes = [IsAuthenticated]

  def get(self, request, format=None):
    resultset = FilterPagination.get_pagination_data(
      request,
      Product,
      ProductSerializer,
      queries=None,
      order_by_array=('-id',)
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
            
            
    serializer = ProductSerializer(item)
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


class ProductCreate(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        author_id = request.user.id
        if not author_id:
            return Response({"error": "L'auteur est requis."}, status=status.HTTP_400_BAD_REQUEST)
        author = get_object_or_404(Member, id=author_id)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=author)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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