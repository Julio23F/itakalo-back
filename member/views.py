from django.db.models import Q, Sum, Max
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema

from utils.pagination_utils import (
  FilterPagination
)

from .models import Member
from .serializers import (
  MemberSerializer,
  FollowingMemberSerializer
)

# from rest_framework.permissions import IsAuthenticated
from authentication.custom_permissions import IsAuthenticated

from utils.member_utils import generate_password, generate_api_key
# from utils.email_utils import send_email_member_password
import uuid
from django.conf import settings

class MemberList(APIView):
  permission_classes = []
  # permission_classes = [IsAuthenticated]
  
  # @swagger_auto_schema(
  #   manual_parameters=FilterPagination.generate_pagination_params(),
  #   responses={200: MemberSerializer(many=True)}
  # )
  def get(self, request, format=None):
    print(f"*********** {request.user}")
    resultset = FilterPagination.get_pagination_data(
      request,
      Member,
      MemberSerializer,
      queries=None,
      order_by_array=('-id',)
    )
    return Response(resultset)


class MemberDetail(APIView):
  def get_object(self, pk=None, user=None):
    try:
      # return Member.objects.get(pk=pk)
      if pk is not None:
          return Member.objects.get(pk=pk)
      elif user is not None:
          return Member.objects.get(pk=user.id)
      else:
          raise Http404
        
    except Member.DoesNotExist:
      raise Http404

  # @swagger_auto_schema(
  #   responses={200: MemberSerializer(many=False)}
  # )
  def get(self, request, pk=None, format=None):
    # item = self.get_object(pk)
    if pk is not None:
        item = self.get_object(pk=pk)
    else:
        item = self.get_object(user=request.user)
            
            
    serializer = MemberSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)

  # @swagger_auto_schema(
  #   request_body=MemberSerializer(many=False),
  #   responses={200: MemberSerializer(many=False)}
  # )
  def put(self, request, pk, format=None):
    item = self.get_object(pk)

    image_file = request.FILES.get('image')
    image_url = None

    print(f"image_file: {image_file}")

    if image_file:
        filename = f"{uuid.uuid4()}_{image_file.name}"
        try:
            settings.SUPABASE.storage.from_("profil_users").upload(filename, image_file.read())

            image_url = settings.SUPABASE.storage.from_("profil_users").get_public_url(filename)
        except Exception as e:
            return Response({"error": "Échec upload Supabase", "details": str(e)}, status=500)

    data = request.data.copy()

    if image_url:
        data['image'] = "https://pynqduobepawjiwemgbm.supabase.co/storage/v1/object/public/profil_users/8159e87b-69bd-45fb-b7ee-1ddc0c9d22de_teeth.png"


    print(f"image_url: {image_url}")
    serializer = MemberSerializer(item, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    item = self.get_object(pk)
    item.delete()
    return Response(status=status.HTTP_200_OK)


class MemberCreate(APIView):
  # @swagger_auto_schema(
  #     request_body=MemberSerializer(many=False),
  #     responses={200: MemberSerializer(many=False)}
  # )
  def post(self, request, format=None):
    serializer = MemberSerializer(data=request.data, many=False)
    if serializer.is_valid():
      # Create new member with serializer
      new_item = Member.objects.create(**serializer.validated_data)


      # Generate password
      new_item.password = generate_password()
     
      new_item.save()
      new_serializer = MemberSerializer(new_item, many=False)
      return Response(new_serializer.data, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

