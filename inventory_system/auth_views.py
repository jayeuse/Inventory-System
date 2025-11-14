from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import OTP
from .gmail_service import gmail_service


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_api(request):
    """
    Step 1: Validate credentials and send OTP.
    
    POST /api/auth/login/
    {
        "username": "your_username",
        "password": "your_password"
    }
    
    Returns OTP session ID if credentials are valid.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        if not user.is_active:
            return Response(
                {'error': 'Account is deactivated'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user has email
        if not user.email:
            return Response(
                {'error': 'No email associated with this account. Please contact administrator.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate OTP
        otp_code = OTP.generate_otp()
        
        # Invalidate any existing unused OTPs for this user
        OTP.objects.filter(user=user, is_used=False, is_verified=False).update(is_used=True)
        
        # Create new OTP record
        otp_record = OTP.objects.create(
            user=user,
            otp=otp_code
        )
        
        # Send OTP via Gmail
        try:
            gmail_service.send_otp_email(
                user_email=user.email,
                username=user.username,
                otp_code=otp_code
            )
        except Exception as e:
            # Delete the OTP record if email fails
            otp_record.delete()
            return Response(
                {'error': f'Failed to send OTP email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'OTP sent to your email',
            'otp_session': str(otp_record.otp_code),
            'email': user.email[:3] + '***@' + user.email.split('@')[1] if '@' in user.email else '***',
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Step 2: Verify OTP and complete login.
    
    POST /api/auth/verify-otp/
    {
        "otp_session": "uuid-from-login-response",
        "otp_code": "123456"
    }
    """
    otp_session = request.data.get('otp_session')
    otp_code = request.data.get('otp_code')
    
    if not otp_session or not otp_code:
        return Response(
            {'error': 'OTP session and code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        otp_record = OTP.objects.get(otp_code=otp_session)
    except OTP.DoesNotExist:
        return Response(
            {'error': 'Invalid OTP session'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if OTP is valid
    if not otp_record.is_valid():
        return Response(
            {'error': 'OTP has expired or already been used'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify OTP code
    if otp_record.otp != otp_code:
        return Response(
            {'error': 'Invalid OTP code'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Mark OTP as verified and used
    otp_record.is_verified = True
    otp_record.is_used = True
    otp_record.save()
    
    # Log the user in
    user = otp_record.user
    login(request, user)
    
    # Get user info and role
    user_info = None
    role = None
    if hasattr(user, 'user_information'):
        user_info = user.user_information
        role = user_info.role
    
    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
            'user_info_id': user_info.user_info_id if user_info else None,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP to user's email.
    
    POST /api/auth/resend-otp/
    {
        "otp_session": "uuid-from-login-response"
    }
    """
    otp_session = request.data.get('otp_session')
    
    if not otp_session:
        return Response(
            {'error': 'OTP session is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        old_otp_record = OTP.objects.get(otp_code=otp_session)
    except OTP.DoesNotExist:
        return Response(
            {'error': 'Invalid OTP session'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = old_otp_record.user
    
    # Mark old OTP as used
    old_otp_record.is_used = True
    old_otp_record.save()
    
    # Generate new OTP
    otp_code = OTP.generate_otp()
    
    # Create new OTP record
    otp_record = OTP.objects.create(
        user=user,
        otp=otp_code
    )
    
    # Send OTP via Gmail
    try:
        gmail_service.send_otp_email(
            user_email=user.email,
            username=user.username,
            otp_code=otp_code
        )
    except Exception as e:
        otp_record.delete()
        return Response(
            {'error': f'Failed to send OTP email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': 'New OTP sent to your email',
        'otp_session': str(otp_record.otp_code),
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_api(request):
    """
    Logout endpoint.
    
    POST /api/auth/logout/
    """
    logout(request)
    return Response(
        {'message': 'Logout successful'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def current_user(request):
    """
    Get current authenticated user info.
    
    GET /api/auth/me/
    """
    user = request.user
    
    if not user.is_authenticated:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user_info = None
    role = None
    if hasattr(user, 'user_information'):
        user_info = user.user_information
        role = user_info.role
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': role,
        'user_info_id': user_info.user_info_id if user_info else None,
        'phone_number': user_info.phone_number if user_info else None,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'is_active': user.is_active,
    }, status=status.HTTP_200_OK)
