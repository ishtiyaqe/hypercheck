from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Product(models.Model):
    product_no = models.CharField(max_length=255, unique=True, null= True)

    name = models.CharField(max_length=255)
    link = models.CharField(max_length=800, null=True, blank=True,  unique=True)
    price = models.CharField(max_length=225, null=True, blank=True)

    Product_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_price(self, request):
        return self.price

    @property
    def code(self):
        return str(self.id)


    class Meta:
        unique_together = [ "name","link"]




class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='product_no')
    image =models.CharField(null=True, max_length=1800)
    image_cover =models.CharField(null=True, max_length=1800,blank=True)
    caption = models.CharField(blank=True, max_length=800, null=True)
    
    
class Review(models.Model):
    product = models.ForeignKey(Product, to_field='product_no', on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=245, null=True, blank=True)
    country = models.CharField(max_length=228, null=True, blank=True)
    review_time = models.CharField(max_length=228, null=True, blank=True)
    review_text = models.TextField()
    review_rating = models.CharField(max_length=50, null=True, blank=True)
    review_title = models.CharField(max_length=255, null=True, blank=True)  # Add this if you also want to store review titles
    verified_purchase = models.BooleanField(default=False, null=True, blank=True)  # Add this if you want to store whether it's a verified purchase

    def __str__(self):
        return f'Review of {self.product.name} by {self.buyer_name}'

class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='product_no',null=True,blank=True)
    query = models.CharField(max_length = 245,null=True,blank=True)
    status = models.CharField(max_length = 245,null=True,blank=True)

class Amazon_login_Details(models.Model):
    username = models.CharField(max_length = 245,null=True,blank=True)
    password = models.CharField(max_length = 245,null=True,blank=True)
    
    

class Amazon_login_Details(models.Model):
    email = models.CharField(max_length = 245,null=True,blank=True)
    password = models.CharField(max_length = 245,null=True,blank=True)
    
class AI_Model(models.Model):
    naive_bayes_classifier = models.FileField(upload_to='models/')
    vectorizer = models.FileField(upload_to='models/')

        