import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import CustomUserModel
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.middleware import csrf
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.cache.backends.base import DEFAULT_TIMEOUT

# Set the cache timeout in seconds (2 minutes in this case)
CACHE_TIMEOUT = 120

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data in the request body'}, status=400)

        # Check if all required fields are provided and not empty
        if email and password and first_name and last_name:
            try:
                # Check if the provided email is valid
                validate_email(email)
            except ValidationError:
                return JsonResponse({'message': 'Invalid email format'}, status=400)

            user = CustomUserModel.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
            response_data = {
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'password':user.password
                }
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'message': 'All fields are required'}, status=400)

    # Return a 405 Method Not Allowed response for other request methods
    return HttpResponse(status=405)

@csrf_exempt
def login_user(request):
   
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON data in the request body'}, status=400)

    if not email or not password:
        return JsonResponse({'message': 'Email and password are required'}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'message': 'Invalid email format'}, status=400)

    try:
        user = CustomUserModel.objects.get(email=email)
    except CustomUserModel.DoesNotExist:
        return JsonResponse({'message': 'User with the provided email does not exist'}, status=401)

    if user.check_password(password):
        login(request, user)
        
        csrf_token = csrf.get_token(request)
        response_data = {
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password':user.password,
                'csrf_token':csrf_token
            }
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'message': 'Invalid credentials'}, status=401)


def logout_user(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

#get user by id
def get_user(request, user_id):
    # Check if the user data exists in the cache
    cache_key = f'user_{user_id}'
    user_data = cache.get(cache_key)

    if user_data is None:
        # If the data is not in the cache, retrieve it from the database
        user = get_object_or_404(CustomUserModel, pk=user_id)
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        # Store the user data in the cache with the specified timeout
        cache.set(cache_key, user_data, CACHE_TIMEOUT)

    return JsonResponse(user_data)


def get_users(request):
    if request.method == 'GET':
        # Get all users from the database
        users = CustomUserModel.objects.all()

        # Serialize the user data to create the JSON response
        user_list = []
        for user in users:
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                # Add any other fields you want to include in the response
            }
            user_list.append(user_data)

        # Return the JSON response with all users
        response_data = {'users': user_list}
        return JsonResponse(response_data)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

