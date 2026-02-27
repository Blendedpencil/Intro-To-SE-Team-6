#Basic Django api framework that handles only logging in. (Django REST API)

#To-DO: add a way to log out at a later date. 
#To-DO: add basic routing
from django.contrib.auth import authenticate, login, logout as auth_logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as auth_logout
from rest_framework.authtoken.models import Token

#Bearer Token Login

# LOGIN 
def login_bearer(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)

            request.session['bearer_token'] = token.key
            request.session['bearer_email'] = email

            return redirect('buyer_page')

        messages.error(request, 'Invalid credentials.')

    return render(request, 'accounts/loginPage.html')


# DASHBOARD
def dash_bearer(request):
    token_key = request.session.get('bearer_token')

    if not token_key:
        return redirect('loginPage')

    try:
        token = Token.objects.select_related('user').get(key=token_key)
    except Token.DoesNotExist:
        messages.error(request, 'Token is invalid or has been revoked.')
        return redirect('loginPage')

    return render(request, 'accounts/buyer_page.html', {
        'email': token.user.username,
        'token': token.key,
    })


# LOGOUT
def logout_bearer(request):
    auth_logout(request)

    token_key = request.session.get('bearer_token')

    request.session.pop('bearer_token', None)
    request.session.pop('bearer_email', None)

    if token_key:
        Token.objects.filter(key=token_key).delete()

    return redirect('loginPage')