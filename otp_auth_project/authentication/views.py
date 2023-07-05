# authentication/views.py

from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import requests

class OTPView(View):
    def get(self, request):
        return render(request, 'authentication/otp_form.html')

    def post(self, request):
        mobile_number = '0000000000'  # Specify the desired mobile number here
        otp = '123456'  # Generate OTP here or use a library like `pyotp`

        user, _ = User.objects.get_or_create(mobile_number=mobile_number)
        user.otp = otp
        user.save()

        # Send OTP via 2Factor.in API
        api_key = 'api kho'  # Replace with your 2Factor.in API key
        url = f"https://2factor.in/API/V1/{api_key}/SMS/{mobile_number}/{otp}/OTP+is+{otp}"
        response = requests.get(url)

        if response.status_code == 200:
            return render(request, 'authentication/otp_verification.html', {'mobile_number': mobile_number})
        else:
            return render(request, 'authentication/otp_form.html', {'error': 'Failed to send OTP'})


class OTPVerificationView(View):
    def post(self, request):
        mobile_number = '0000000000'  # Specify the desired mobile number here
        otp = request.POST.get('otp')

        try:
            user = User.objects.get(mobile_number=mobile_number, otp=otp)
            # Perform further authentication or login logic here
            return render(request, 'authentication/success.html')
        except User.DoesNotExist:
            return render(request, 'authentication/otp_verification.html', {'mobile_number': mobile_number, 'error': 'Invalid OTP'})


class UserListAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
