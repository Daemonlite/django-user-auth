import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import CustomUserModel
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpResponse


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

        response_data = {
            'message': 'Logged in successfully',
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
        return JsonResponse({'message': 'Invalid credentials'}, status=401)

@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

@csrf_exempt
def get_user(request, user_id):
    user = get_object_or_404(CustomUserModel, pk=user_id)
    data = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    return JsonResponse(data)
