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



class FollowMultipleMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get("member_ids", [])
        if not isinstance(ids, list):
            return Response({'error': 'member_ids doit être une liste'}, status=status.HTTP_400_BAD_REQUEST)

        current_user = request.user
        followed_count = 0

        print(f"ids, {ids}")
        
        for member_id in ids:
            try:
                member = Member.objects.get(id=member_id)
                if member != current_user:
                    current_user.following.add(member)
                    followed_count += 1
            except Member.DoesNotExist:
                continue

        return Response({'message': f'{followed_count} membres suivis.', 'followed': True})



class UnfollowMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        current_user = request.user

        try:
            member = Member.objects.get(id=pk)

            if member == current_user:
                return Response({'error': "Vous ne pouvez pas vous désuivre vous-même."},
                                status=status.HTTP_400_BAD_REQUEST)

            current_user.following.remove(member)
            return Response({'message': f'Vous ne suivez plus {member.first_name} {member.last_name}.', 'unfollowed': True})
        
        except Member.DoesNotExist:
            return Response({'error': "Membre introuvable."}, status=status.HTTP_404_NOT_FOUND)
          
          
      
class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        following = user.following.all()
        serializer = MemberSerializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
      

class SaveExpoTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        token = request.data.get("token")
        if not token:
            return Response({'error': 'Le token est requis'}, status=status.HTTP_400_BAD_REQUEST)

        member = request.user
        member.expo_push_token = token
        member.save()

        return Response({'message': 'Token enregistré avec succès'}, status=status.HTTP_200_OK)


