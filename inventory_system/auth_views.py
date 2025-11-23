from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import OTP
from .services.gmail_service import gmail_service


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


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def check_username(request):
    """
    Check if username exists (for forgot password flow).
    
    POST /api/auth/check-username/
    {
        "username": "your_username"
    }
    
    Returns user existence status without sensitive information.
    """
    username = request.data.get('username')
    
    if not username:
        return Response(
            {'error': 'Username is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
        
        if not user.is_active:
            return Response(
                {'error': 'Account is deactivated'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not user.email:
            return Response(
                {'error': 'No email associated with this account. Please contact administrator.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return masked email
        email_parts = user.email.split('@')
        masked_email = user.email[:3] + '***@' + email_parts[1] if '@' in user.email else '***'
        
        return Response({
            'exists': True,
            'email': masked_email
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Username not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request password reset and send OTP.
    
    POST /api/auth/request-password-reset/
    {
        "username": "your_username"
    }
    
    Sends OTP to user's email for password reset.
    """
    username = request.data.get('username')
    
    if not username:
        return Response(
            {'error': 'Username is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
        
        if not user.is_active:
            return Response(
                {'error': 'Account is deactivated'},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
                otp_code=otp_code,
                is_password_reset=True
            )
        except Exception as e:
            otp_record.delete()
            return Response(
                {'error': f'Failed to send OTP email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Password reset OTP sent to your email',
            'reset_session': str(otp_record.otp_code),
            'email': user.email[:3] + '***@' + user.email.split('@')[1] if '@' in user.email else '***',
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Username not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_reset_otp(request):
    """
    Verify OTP for password reset.
    
    POST /api/auth/verify-reset-otp/
    {
        "reset_session": "uuid-from-request-response",
        "otp_code": "123456"
    }
    
    Returns success if OTP is valid.
    """
    reset_session = request.data.get('reset_session')
    otp_code = request.data.get('otp_code')
    
    if not reset_session or not otp_code:
        return Response(
            {'error': 'Reset session and OTP code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        otp_record = OTP.objects.get(otp_code=reset_session)
    except OTP.DoesNotExist:
        return Response(
            {'error': 'Invalid reset session'},
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
    
    # Mark OTP as verified (but NOT used yet - will be used after password reset)
    otp_record.is_verified = True
    otp_record.save()
    
    return Response({
        'message': 'OTP verified successfully',
        'reset_session': reset_session
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password after OTP verification.
    
    POST /api/auth/reset-password/
    {
        "reset_session": "uuid-from-verify-response",
        "new_password": "new_password",
        "confirm_password": "new_password"
    }
    
    Resets user's password.
    """
    reset_session = request.data.get('reset_session')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not all([reset_session, new_password, confirm_password]):
        return Response(
            {'error': 'All fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_password != confirm_password:
        return Response(
            {'error': 'Passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        otp_record = OTP.objects.get(otp_code=reset_session)
    except OTP.DoesNotExist:
        return Response(
            {'error': 'Invalid reset session'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if OTP was verified and not expired
    if not otp_record.is_verified:
        return Response(
            {'error': 'OTP not verified'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if otp_record.is_used:
        return Response(
            {'error': 'Reset session already used'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if OTP has expired (can't use is_valid() since is_verified is True)
    if timezone.now() >= otp_record.expires_at:
        return Response(
            {'error': 'Reset session has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Reset the password
    user = otp_record.user
    user.set_password(new_password)
    user.save()
    
    # Mark OTP as used
    otp_record.is_used = True
    otp_record.save()
    
    # Send confirmation email
    try:
        gmail_service.send_password_reset_success_email(
            user_email=user.email,
            username=user.username
        )
    except Exception as e:
        # Log error but don't fail the password reset
        print(f"Failed to send password reset confirmation email: {str(e)}")
    
    return Response({
        'message': 'Password reset successfully'
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def resend_reset_otp(request):
    """
    Resend OTP for password reset.
    
    POST /api/auth/resend-reset-otp/
    {
        "reset_session": "uuid-from-request-response"
    }
    """
    reset_session = request.data.get('reset_session')
    
    if not reset_session:
        return Response(
            {'error': 'Reset session is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        old_otp_record = OTP.objects.get(otp_code=reset_session)
    except OTP.DoesNotExist:
        return Response(
            {'error': 'Invalid reset session'},
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
            otp_code=otp_code,
            is_password_reset=True
        )
    except Exception as e:
        otp_record.delete()
        return Response(
            {'error': f'Failed to send OTP email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': 'New password reset OTP sent to your email',
        'reset_session': str(otp_record.otp_code),
    }, status=status.HTTP_200_OK)
