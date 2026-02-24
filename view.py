#Basic Django api framework that handles only logging in. (Django REST API)

#To-DO: add a way to log out at a later date. 
#To-DO: add basic routing
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class LoginView(APIView):
    """
    {
        "email": "example",
        "password": "password123"
    }
    """

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Check if the fields are filled in
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Authenticate user
        # Whenever value is stored in the email variable, it'll pass as Django's username field for Auth
        user = authenticate(request, Username=email, password=password)

        #Only accounts for if the login field is empty or not. Not made to handle a duplicate email yet because no database yet
        if user is not None:
            login(request, user)
            return Response(
                {"message": "Login successful"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )