from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import status  
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404  
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from musix.models import AudioFile
from musix.models import AudioFile








@api_view(['POST'])

def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request,username=username,password=password)

    if user is not None:
        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "message": "Login successful!",
                "token": token.key  # Send the token as a response
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Your account is not active. Please confirm your email."
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response ({"You are trash"}, status=status.HTTP_404_NOT_FOUND)
    


#user logout

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    user = request.user
    username = user.username

    try:
        user.auth_token.delete()
    except:
        return Response({'error': 'Token not found or already deleted.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'User logged out successfully', 'username': username}, status=status.HTTP_200_OK)


        






### Backup code

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings



@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.is_active = False
        user.save()



        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct the confirmation link
        confirmation_link = f"http://127.0.0.1:8000/api/confirm/{uid}/{token}"


       

        subject = "Confirm Your Email Address"
        message = render_to_string("email/confirmation_email.html", {'user': user, 'confirmation_link': confirmation_link})
        
       
        send_mail(
            subject,
            message, 
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=message,  
        )

        return Response({"message": "Please check your email to confirm your account."}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





        ##return Response({'Token':token.key, 'serializer':serializer.data})
    ##return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def test_token(request):
    return Response({})

from django.shortcuts import redirect

@api_view(['GET'])
def confirm_email(request, uidb64, token):
    try:
        print("uid",uidb64)
        print("token",token)

        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        
        # Validate the token
        if default_token_generator.check_token(user, token):
            user.is_active = True  
            user.save()
            return redirect("http://localhost:5173/email-confirmed")
        else:
            return Response({"message": "Invalid confirmation link or token."}, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    



#Forgot Password Process

from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User

@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"http://localhost:5173/api/password-reset-confirm/{uid}/{token}/" ####edited this part

        subject = "Reset your password"

        # ✅ Create a real clickable HTML message
        html_message = f"""
        <html>
          <body>
            <p>Click the button below to reset your password:</p>
            <p><a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background-color: #3db4ff; color: white; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
          </body>
        </html>
        """

        plain_message = strip_tags(html_message)  # fallback for email clients that don't render HTML

        email_message = EmailMessage(
            subject,
            html_message,
            from_email=None,
            to=[email],
        )
        email_message.content_subtype = "html"  # This is the important part!

        email_message.send()

        return Response({"message": "Password reset email sent!"})
    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist."}, status=400)

#confirm reset password

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful."})
        else:
            return Response({"error": "Invalid token."}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

#users can search and admin can upload


from rest_framework import generics, permissions, filters
from musix.serializers import AudioFileSerializer
from musix.models import AudioFile

from rest_framework import generics, permissions
from musix.models import AudioFile
from .serializers import AudioFileSerializer

# List all uploaded songs (for normal user dashboard)


# Only Admins can Upload Songs
class AudioFileUploadView(generics.CreateAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can upload

from rest_framework import filters

 # Search by name, mood, lyrics


from rest_framework import generics, permissions, filters
from musix.models import AudioFile

from .serializers import AudioFileSerializer

# Only Admins can Upload Songs
class AudioFileUploadView(generics.CreateAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can upload

# All users can Search and Listen to Songs
class AudioFileListView(generics.ListAPIView):
    queryset = AudioFile.objects.filter(confirmed=True)
    serializer_class = AudioFileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Any logged-in user
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'mood', 'lyrics']  # Search by name, mood, lyrics


@api_view(['GET'])
def check_email_confirmation(request):
    email = request.query_params.get('email')
    if not email:
        return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_user_model().objects.get(email=email)
        if user.is_active:
            return Response({"message": "Email confirmed.", "username": user.username}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Email not confirmed yet. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)
    except ObjectDoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    


    #admin login

    from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user and user.is_staff:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "is_admin": True,
            "username": user.username
        })
    return Response({"error": "Invalid credentials or not an admin"}, status=status.HTTP_403_FORBIDDEN)


##