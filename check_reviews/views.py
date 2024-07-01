import decimal
from django.shortcuts import get_object_or_404
from django.contrib import messages
import os
import re
import time
from cmath import exp
from decimal import *
from http.client import EXPECTATION_FAILED
# from importlib.resources import path
from multiprocessing import context
from urllib import request
# from attrs import attr
import requests
import datetime
from django.conf import settings
import re
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.db.models import Avg, Count, Max, Min
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
# paypal
from django.urls import URLPattern, reverse
from django.views.decorators.csrf import csrf_exempt
# required imports
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import joblib
from rest_framework.settings import api_settings
from rest_framework.test import APIClient
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view
import uuid
import json
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.serializers import serialize
from urllib.parse import urlparse
from .models import *
from .amazon_api import *
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status, permissions, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import permission_classes, authentication_classes
from decimal import Decimal, ROUND_HALF_UP
import threading
from .validations import *
# Create your views here.


@login_required
def search(request):
    user = request.user.id
    if request.method == 'GET':
        query = request.GET.get('query')


       
        validate = URLValidator()


        try:

            x = query
            # Define a regular expression pattern to match URLs
            url_pattern = r'https?://\S+'

            # Find all matches in the string
            matches = re.findall(url_pattern, x)

            # Check if any URLs were found and take the first one
            if matches:
                link = matches[0]
            else:
                link = None

            print(link)
            validate(link)

            try:
                      
                if "amazon.com" in link or "a.co" in link:
                    products = Product.objects.filter(link__icontains=link)
                    print("amazon call")
                    if products:
                        product_list = product_class(products, user, x)
                        print("amazon pricelist call")
                        return JsonResponse({'products': product_list})
                    else:
                        
                        threading.Thread(target=thread_function, args=(link,user)).start()

                                    
                                    
                products = Product.objects.filter(link__icontains = link)
                product_list = product_class(products, user, x)
                return JsonResponse({'products': product_list})
    
                 
            except IntegrityError:

                if query:
                    products = Product.objects.filter(link__icontains=x)
                    product_list = []
                    product_list = product_class(products)
                    return JsonResponse({'products': product_list})

                else:

                    products = Product.objects.filter(name__icontains=query)
                    product_list = product_class(products)
                    return JsonResponse({'products': product_list})



        except:
            try:
                search_query = SearchQuery.objects.get(query=query)
            except:
                search_query = SearchQuery(query=x, status='Searching')
                search_query.save()
                search_query = SearchQuery.objects.get(query=query)
            
try:
    ab =  AI_Model.objects.last() 
    # Load the trained model and vectorizer
    naive_bayes_classifier = joblib.load(ab.naive_bayes_classifier)
    vectorizer = joblib.load(ab.vectorizer)
except:
    # Load the trained model and vectorizer
    naive_bayes_classifier = joblib.load('Naive_Bayes.pkl')
    vectorizer = joblib.load('Count_Vectorizer.pkl')
    

def clean_product_title(title):
    stripped_title = title.strip()
    cleaned_title = re.sub(r'\s+', ' ', stripped_title)
    return cleaned_title


def product_class(products, user, x):
    product_list = []
    for product in products:
        SearchQuery.objects.create(query=x, user_id=user,product=product,status='Completed')

        reviews = Review.objects.filter(product=product)
        serialized_reviews = []
        
        for review in reviews:
            # Classify the review
            classification_result = classify_review(review.review_text)
            
            # Serialize the review data
            serializer = ReviewSerializer(review)
            serialized_data = serializer.data
            
            # Add classification result to serialized data
            serialized_data['classification_result'] = classification_result
            
            # Append serialized review data to list
            serialized_reviews.append(serialized_data)
        
        # Construct product data
        product_data = {
            'id': product.id,
            'product_no': product.product_no,
            'name': clean_product_title(product.name),
            'link': product.link,
            'reviews': serialized_reviews,
        }
        
        first_image = ProductImage.objects.filter(product=product).first()
        second_image = ProductImage.objects.filter(product=product)[1:2]  # Fetches the second image if it exists

        # Initialize image field
        product_data['image'] = ''

        if first_image:
            if 'https://video01' in first_image.image:
                if second_image.exists():
                    product_data['image'] = second_image.first().image
                else:
                    product_data['image'] = first_image.image_cover
            else:
                product_data['image'] = first_image.image
        
        # Append product data to product list
        product_list.append(product_data)
    
    return product_list


def calculate_grade(cd_count, total_reviews):
    if total_reviews == 0:
        return "Not Rated"
    
    percentage_cd = (cd_count / total_reviews) * 100
    
    if percentage_cd >= 90:
        return "A+"
    elif percentage_cd >= 80:
        return "A"
    elif percentage_cd >= 70:
        return "B+"
    elif percentage_cd >= 60:
        return "B"
    elif percentage_cd >= 50:
        return "C+"
    else:
        return "C"
    
    

def product(request, id):
    
    product_list = []
    product = Product.objects.get(id=id)
    reviews = Review.objects.filter(product=product)
    serialized_reviews = []
    cd_count = 0   # Initialize counts for OR (fake) reviews
    for review in reviews:
        # Classify the review
        classification_result = classify_review(review.review_text)
        # Determine if review is genuine (CD)
        if classification_result == "CG":
            cd_count += 1
        # Serialize the review data
        serializer = ReviewSerializer(review)
        serialized_data = serializer.data
        
        # Add classification result to serialized data like is genien is = "CG" or fake will be ="OR" 
        serialized_data['classification_result'] = classification_result
        
        # Append serialized review data to list
        serialized_reviews.append(serialized_data)
    total_reviews = reviews.count()
    # Calculate grade based on genuine review percentage
    grade = calculate_grade(cd_count, total_reviews)
    # Construct product data
    product_data = {
        'id': product.id,
        'price': product.price,
        'product_no': product.product_no,
        'name': clean_product_title(product.name),
        'link': product.link,
        'grade': grade,
        'reviews': serialized_reviews,
    }
    print(grade)
    print(cd_count)
    first_image = ProductImage.objects.filter(product=product).first()
    second_image = ProductImage.objects.filter(product=product)[1:2]  # Fetches the second image if it exists

    # Initialize image field
    product_data['image'] = ''

    if first_image:
        if 'https://video01' in first_image.image:
            if second_image.exists():
                product_data['image'] = second_image.first().image
            else:
                product_data['image'] = first_image.image_cover
        else:
            product_data['image'] = first_image.image
    
    # Append product data to product list
    product_list.append(product_data)

    return JsonResponse(product_data)


class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)

   
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)


def classify_review(review_text):
    # Vectorize the review text using the loaded CountVectorizer
    review_vectorized = vectorizer.transform([review_text])
    
    # Predict the label (genuine or fake/sarcastic)
    prediction = naive_bayes_classifier.predict(review_vectorized)[0]
    
    return prediction  

def producta_list(products):
    product_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'product_no': product.product_no,
            'name': product.name,
            'link': product.link,
        }

        first_image = ProductImage.objects.filter(product=product).first()
        last_image = ProductImage.objects.filter(product=product).last()   
        if first_image:
            if 'https://video01' in first_image.image:
                product_data['image'] = first_image.image_cover
            else:
                product_data['image'] = last_image.image
        else:
            product_data['image'] = ''

        product_list.append(product_data)

    return product_list



import asyncio    
def thread_function(x,user):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(amazon_api(x,user))






from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.models import SocialAccount
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from allauth.socialaccount.helpers import complete_social_login
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth import authenticate

class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	##
	def get(self, request):
		serializer = UserSerializer(request.user)
		return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    
class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        serializer = UserLoginSerializer(data=data)

        if not username or not password:
            return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            error_message = 'User not found or incorrect password'
            return Response({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
        
        

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        # Perform Google login
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            # Google login successful, retrieve the user data
            token_key = response.data.get('key')
            if token_key:
                try:
                    # Query the SocialToken model to find the user associated with the provided key
                    social_token = Token.objects.get(key=token_key)
                    user = social_token.user

                    # Authenticate and log in the user
                    if user:
                        user = authenticate(request=request, username=user.username)
                        login(request, user)
                        return Response({'message': 'Login successful','key':token_key}, status=status.HTTP_200_OK)
                    else:
                        error_message = 'User not found'
                        return Response({'error': error_message}, status=status.HTTP_404_NOT_FOUND)
                except Token.DoesNotExist:
                    error_message = 'Social token does not exist'
                    return Response({'error': error_message}, status=status.HTTP_404_NOT_FOUND)
        return response
      
    
    
class UserLogout(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


    
class MyAccountView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request, format=None):
        user = request.user

        # Fetch all search queries associated with the current user
        search_queries = SearchQuery.objects.filter(user=user)

        # Serialize the search queries
        search_query_data = []
        for query in search_queries:
            search_query_data.append({
                'query': query.query,
                'status': query.status,
                'product': ProductSerializer(query.product).data if query.product else None,
            })

        # Serialize the user data
        user_serializer = UserSerializer(user)

        # Return the serialized data
        return Response({
            'user': user_serializer.data,
            'search_queries': search_query_data,
        })
        
        

