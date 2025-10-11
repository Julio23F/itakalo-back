from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from member.models import Member
# from dentist_profile.models import DentistProfile
from member.serializers import MemberSerializer
from .serializers import (
  LoginSerializer,
  RegisterSerializer,
  RegisterByEmailSerializer,
  ForgetPasswordSerializer,
  ChangeEmailSerializer,
  ChangePasswordSerializer,
  GoogleAuthSerializer
)
from .custom_admin_jwt import (
  custom_admin_authentication,
  admin_jwt_payload_handler,
  admin_jwt_encode_handler
)
from .custom_jwt import (
  jwt_payload_handler,
  jwt_encode_handler
)
from email_verification import send_email, send_email_password_reset, send_email_reset, send_password_reset
from lib.loguru import logger
from email_verification.confirm import verify_token
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from datetime import datetime

from rest_framework.permissions import AllowAny

from django.db import models

class GoogleLoginAPIView(APIView):
    """
    Endpoint pour la connexion avec Google OAuth
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def verify_google_token(self, token):
        """
        Vérifie le token Google et retourne les informations de l'utilisateur
        """
        try:
            # Vérifier le token avec Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_OAUTH_CLIENT_ID
            )
            
            # Vérifier que le token provient bien de Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Vérifier le domaine si nécessaire
            if hasattr(settings, 'GOOGLE_OAUTH_ALLOWED_DOMAINS') and settings.GOOGLE_OAUTH_ALLOWED_DOMAINS:
                email_domain = idinfo['email'].split('@')[1]
                if email_domain not in settings.GOOGLE_OAUTH_ALLOWED_DOMAINS:
                    raise ValueError(f'Domain {email_domain} not allowed.')
            
            return idinfo
            
        except ValueError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            raise AuthenticationFailed(f'Token verification failed: {str(e)}')
    
    def get_or_create_user(self, google_data):
        """
        Récupère ou crée un utilisateur à partir des données Google
        """
        email = google_data.get('email')
        google_id = google_data.get('sub')
        
        # Chercher l'utilisateur par email ou google_id
        member = Member.objects.filter(
            models.Q(email=email) | models.Q(google_id=google_id)
        ).first()
        
        if member:
            # Mettre à jour les informations si nécessaire
            if not member.google_id:
                member.google_id = google_id
            member.is_google_user = True
            member.profile_picture = google_data.get('picture')
            member.login_date = datetime.now()
            member.save()
        else:
            # Créer un nouveau membre
            member = Member.objects.create(
                email=email,
                google_id=google_id,
                first_name=google_data.get('given_name', ''),
                last_name=google_data.get('family_name', ''),
                username=email.split('@')[0],  # Générer un username
                profile_picture=google_data.get('picture'),
                is_google_user=True,
                login_date=datetime.now()
            )
        
        return member
    
    def post(self, request):
        """
        POST /api/auth/google/
        Body: { "token": "google_id_token" }
        """

        print("POST /api/auth/google/")
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Vérifier le token Google
        google_data = self.verify_google_token(serializer.validated_data['token'])
        
        # Créer ou récupérer l'utilisateur
        member = self.get_or_create_user(google_data)
        
        print(f"+++++++++++++ member {member}")

        # Générer le JWT token
        payload = jwt_payload_handler(member)
        token = jwt_encode_handler(payload)
        
        return Response({
            'token': token,
            'member': MemberSerializer(member).data,
            'message': 'Connexion réussie'
        }, status=status.HTTP_200_OK)




class CustomLogin(APIView):
    permission_classes = []

    def process_admin_user(self, request, admin, serializer):
      admin_user = custom_admin_authentication(
        request, 
        email=serializer.data['email'],
        password=serializer.data['password']
      )
      if admin_user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
      else:
        payload = admin_jwt_payload_handler(admin_user)
        # Generate admin jwt token
        token = admin_jwt_encode_handler(payload)
        return Response({'token': token, 'member': payload})

    def process_member(self, request, member, serializer):
      if (member.password != serializer.data['password']) and (not serializer.data['email'] is None):
        raise AuthenticationFailed('Identifiants invalides, veuillez réessayer.')
        # return Response(status=status.HTTP_401_UNAUTHORIZED)
      
      # dentist_profile = DentistProfile.objects.filter(dentist=member).first()
      # if dentist_profile:
      #     dentist_profile.check_discount_expiry()
      member.login_date = datetime.now()
      member.save()
      payload = jwt_payload_handler(member)
      token = jwt_encode_handler(payload)
      return Response({'token': token, 'member': payload})


    def get_client_ip(self, request):
      # Priorité 1 : Cloudflare
      ip = request.META.get('HTTP_CF_CONNECTING_IP')
      if ip:
          return ip

      # Priorité 2 : X-Forwarded-For
      x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
      if x_forwarded_for:
          return x_forwarded_for.split(',')[0].strip()

      # Sinon : REMOTE_ADDR
      return request.META.get('REMOTE_ADDR')


    @swagger_auto_schema(
        request_body=LoginSerializer(many=False),
        responses={200: MemberSerializer(many=False)}
    )
    def post(self, request, format=None, *args, **kwargs):
      serializer = LoginSerializer(
        data=request.data,
        context={'request': request}
      )
      ip = request.META.get('REMOTE_ADDR')
      client_ip = self.get_client_ip(request)
      print(f"📌 Client IP: {client_ip}")
      
      print(f"request ***************** {request.data}")
      print(f"ip ***************** {ip}")
      
      serializer.is_valid(raise_exception=True)
      member = None
      
      if ('email' in serializer.data) and (not serializer.data['email'] is None):
        # Check members for general user.
        member = Member.objects.filter(email__iexact=serializer.data['email']).first()
      print(f"member {member}")
      if member is None:
        # Check admin user.
        admin = User.objects.filter(email__iexact=serializer.data['email']).first()
        if admin is None:
          return Response(status=status.HTTP_404_NOT_FOUND)
        return self.process_admin_user(request, admin, serializer)


      # Generate member jwt token
      return self.process_member(request, member, serializer)


# class CustomLoginByEmail(APIView):
#     permission_classes = []

#     def process_admin_user(self, request, admin, serializer):
#       admin_user = custom_admin_authentication(
#         request, 
#         email=serializer.data['email'],
#         password=serializer.data['password']
#       )
#       if admin_user is None:
#         return Response(status=status.HTTP_401_UNAUTHORIZED)
#       else:
#         payload = admin_jwt_payload_handler(admin_user)
#         # Generate admin jwt token
#         token = admin_jwt_encode_handler(payload)
#         return Response({'token': token, 'member': payload})

#     def process_member(self, request, member, serializer):
#       if member.password != serializer.data['password']:
#         return Response(status=status.HTTP_401_UNAUTHORIZED)
#       member.login_date = datetime.now()
#       member.save()
#       payload = jwt_payload_handler(member)
#       token = jwt_encode_handler(payload)
#       return Response({'token': token, 'member': payload})

#     @swagger_auto_schema(
#         request_body=LoginSerializer(many=False),
#         responses={200: MemberSerializer(many=False)}
#     )
#     def post(self, request, format=None):
#       serializer = LoginSerializer(
#         data=request.data,
#         context={'request': request}
#       )
#       serializer.is_valid(raise_exception=True)
#       email = serializer.data['email'] if ('email' in serializer.data) else None
#       udid = serializer.data['udid'] if ('udid' in serializer.data) else None
#       member = Member.objects.filter(email=serializer.data['email']).first()
#       if member is None:
#         # Check admin user.
#         admin = User.objects.filter(email=serializer.data['email']).first()
#         if admin is None:
#           return Response(status=status.HTTP_404_NOT_FOUND)
#         return self.process_admin_user(request, admin, serializer)

#       # Generate member jwt token
#       return self.process_member(request, member, serializer)


class Logout(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # simply delete the token to force a login
        user = request.user
        try:
            if hasattr(user, 'auth_token'):
              user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist) as ex:
            logger.error(f'logout error: {str(ex)} on {ex.__traceback__.tb_lineno} line')
        
        return Response({}, status=status.HTTP_200_OK)


class Register(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=RegisterSerializer(many=False),
        responses={200: MemberSerializer(many=False)}
    )
    def post(self, request, format=None):      
      serializer = RegisterSerializer(data=request.data, many=False)
      if serializer.is_valid():
        # if 'udid' in serializer.data:
        #   item = Member.objects.filter(udid=serializer.data['udid']).first()
        #   item_serializer = MemberSerializer(item, many=False)
        #   if item:
        #     return Response(item_serializer.data, status=status.HTTP_201_CREATED)
        new_item = Member(**serializer.validated_data)
        new_item.save()
        new_serializer = MemberSerializer(new_item, many=False)
        return Response(new_serializer.data, status=status.HTTP_201_CREATED)
      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ChangeUserInfo(APIView):
  permission_classes = []

  @swagger_auto_schema(
      request_body=RegisterSerializer(many=False),
      responses={200: MemberSerializer(many=False)}
  )

  def post(self, request, format=None):      
    serializer = LoginSerializer(
      data=request.data,
      context={'request': request}
    )
    serializer.is_valid(raise_exception=True)

    is_member = None
    if ('email' in serializer.data) and (not serializer.data['email'] is None):  
      # Check members for general user.
      is_member = Member.objects.filter(email=serializer.data['email']).first()

    if is_member is None:
      # Check admin user.
      member = Member.objects.filter(udid=serializer.data['udid']).first()
      if member is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
      else:
        member.email = serializer.data['email']
        member.password = serializer.data['password']
        member.save()
        payload = jwt_payload_handler(member)
        token = jwt_encode_handler(payload)
        return Response({'token': token, 'member': payload})

    return Response(status=status.HTTP_404_NOT_FOUND)


class RegisterByEmail(APIView):
    permission_classes = []
    
    def update_and_resend_verifiction_token(self, request, member):
      member_serializer = MemberSerializer(member, request.data)
      if member_serializer.is_valid():
        member_serializer.save()
        member.save()
        send_email(member)
        return Response(member_serializer.validated_data, status=status.HTTP_200_OK)
      else:
        return Response({'error': member_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=RegisterByEmailSerializer(many=False),
        responses={200: MemberSerializer(many=False)}
    )
    def post(self, request, format=None):      
      serializer = RegisterByEmailSerializer(data=request.data, many=False)
      if serializer.is_valid():
        # Check validation
        email = serializer.data['email'] if 'email' in serializer.data else None
        udid = serializer.data['udid'] if 'udid' in serializer.data else None
        if email is None:
          return Response({'email': ['Missed email field',]}, status=status.HTTP_400_BAD_REQUEST)
        if udid is None:
          return Response({'udid': ['Missed udid field.',]}, status=status.HTTP_400_BAD_REQUEST)
        
        member = Member.objects.filter(email=email).first()
        if member:
          if member.confirmed:
            # If member already registered and confirmed, skip.
            return Response({'error': 'Member with this email address already exists.'}, status=status.HTTP_400_BAD_REQUEST)
          else:
            # If member already was registered and not confirmed,
            # update with body and send verification token via email.
            return self.update_and_resend_verifiction_token(request, member)
        else:
          # If member not exist, check udid.)
          member = Member.objects.filter(udid=udid).first()
          if member is None:
            # create new member record and send verification token via email
            new_member = Member(**serializer.validated_data)
            new_member.save()
            # send_email(new_member)
            new_serializer = MemberSerializer(new_member, many=False)
            return Response(new_serializer.data, status=status.HTTP_201_CREATED)

          if member.confirmed:
            return Response({'error': 'Member with this email address already exists.'}, status=status.HTTP_400_BAD_REQUEST)
          else:
            return self.update_and_resend_verifiction_token(request, member)

      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPassword(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=ForgetPasswordSerializer(many=False),
        responses={200: {}}
    )
    def post(self, request, format=None):      
      serializer = ForgetPasswordSerializer(data=request.data, many=False)
      if serializer.is_valid():
        # Check validation
        email = serializer.data['email'] if 'email' in serializer.data else None
        if email is None:
          return Response({'email': ['Missed email field',]}, status=status.HTTP_400_BAD_REQUEST)
        
        member = Member.objects.filter(email=email).first()
        if member:
          # if member.confirmed:
          send_email_password_reset(member, is_forget_password_request = True)
          return Response({'result': 'A reset password email has been sent to ' + email + '.'}, status=status.HTTP_200_OK)
          # else:
          #   return Response({'error': 'Member with this email address was not verifyed yet.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
          return Response({'error': 'Member with this email address don\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ChangeUserInfoMail(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=ChangeEmailSerializer(many=False),
        responses={200: {}}
    )
    def post(self, request, format=None):      
      serializer = ChangeEmailSerializer(data=request.data, many=False)
      if serializer.is_valid():
        # Check validation
        email = serializer.data['email'] if 'email' in serializer.data else None
        if email is None:
          return Response({'email': ['Missed email field',]}, status=status.HTTP_400_BAD_REQUEST)
        
        member = Member.objects.filter(email=email).first()
        if member:
          if member.confirmed:
            send_email_reset(member, serializer.data['new_email'])
            return Response({'result': 'A reset password email has been sent to ' + email + '.'}, status=status.HTTP_200_OK)
          else:
            return Response({'error': 'Member with this email address was not verifyed yet.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
          return Response({'error': 'Member with this email address don\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ChangeUserInfoPassword(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer(many=False),
        responses={200: {}}
    )
    def post(self, request, format=None):      
      serializer = ChangePasswordSerializer(data=request.data, many=False)
      if serializer.is_valid():
        # Check validation
        email = serializer.data['email'] if 'email' in serializer.data else None
        if email is None:
          return Response({'email': ['Missed email field',]}, status=status.HTTP_400_BAD_REQUEST)
        
        member = Member.objects.filter(email=email).first()
        if member:
          if member.confirmed:
            send_password_reset(member, serializer.data['new_password'])
            return Response({'result': 'A reset password email has been sent to ' + email + '.'}, status=status.HTTP_200_OK)
          else:
            return Response({'error': 'Member with this email address was not verifyed yet.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
          return Response({'error': 'Member with this email address don\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ChangeUserResetPassword(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer(many=False),
        responses={200: {}}
    )

    def post(self, request, format=None):      
      serializer = ChangePasswordSerializer(data=request.data, many=False)
      if serializer.is_valid():
        # Check validation
        email = serializer.data['email'] if 'email' in serializer.data else None
        if email is None:
          return Response({'email': ['Missed email field',]}, status=status.HTTP_400_BAD_REQUEST)
        
        member = Member.objects.filter(email=email).first()
        if member:
          if member.confirmed:
            member.password = serializer.data['new_password']
            member.save()
            return Response({'result': 'Password reset successfully'}, status=status.HTTP_200_OK)
          else:
            return Response({'error': 'Member with this email address was not verifyed yet.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
          return Response({'error': 'Member with this email address don\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class VerifyResetPasswordToken(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer(many=False),
        responses={200: {}}
    )

    def post(self, request, format=None):
      token = request.data['token']
      if token:
        success, member = verify_token(token)
        member_id = member.id if member else 0
        # new_email = member.new_email if member else None
        new_email = None
        member_email = member.email if member else None  

        if member_id:
          return Response({
            'success': success,
            'member_id': member_id,
            'member_email': member_email,
          }, status=status.HTTP_200_OK)
        else:
          return Response({
            'success': False,
          }, status=status.HTTP_200_OK)


      return Response({'error': "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST) 
