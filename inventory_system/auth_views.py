from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """
    Login endpoint for API authentication.
    
    POST /api/auth/login/
    {
        "username": "your_username",
        "password": "your_password"
    }
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
    else:
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


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
