from rest_framework import serializers
from .models import *

class ReviewSerializer(serializers.ModelSerializer):
    classification_result = serializers.CharField(max_length=10, required=False)  # Adjust max_length and required as per your needs

    class Meta:
        model = Review
        fields = ['id', 'product', 'buyer_name', 'country', 'review_time', 'review_text',
                  'review_rating', 'review_title', 'verified_purchase', 'classification_result']
        
        
        
from xml.dom import ValidationErr
from rest_framework import serializers
from .models import *
# serializers.py
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate

UserModel = get_user_model()



class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ('email', 'username')

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = '__all__'
	def create(self, clean_data):
		user_obj = UserModel.objects.create_user(username=clean_data['username'], password=clean_data['password'])
		user_obj.username = clean_data['username']
		user_obj.save()
		return user_obj

class UserLoginSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField()
	##
	def check_user(self, clean_data):
		user = authenticate(username=clean_data['username'], password=clean_data['password'])
		if not user:
			raise ValidationError({'error': 'User not found'}, code=status.HTTP_404_NOT_FOUND)
		return user



from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = '__all__'
	def create(self, clean_data):
		user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
		user_obj.username = clean_data['username']
		user_obj.save()
		return user_obj

class UserLoginSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField()
	##
	def check_user(self, clean_data):
		user = authenticate(username=clean_data['email'], password=clean_data['password'])
		if not user:
			raise ValidationError('user not found')
		return user

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ('id','email', 'username')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'image_cover', 'caption']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['buyer_name', 'country', 'review_time', 'review_text', 'review_rating', 'review_title', 'verified_purchase']

class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True, source='review_set')
    images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')  # Assuming related name is productimage_set

    class Meta:
        model = Product
        fields = ['id','product_no', 'name', 'link', 'price', 'Product_id', 'created_at', 'updated_at', 'reviews','images']