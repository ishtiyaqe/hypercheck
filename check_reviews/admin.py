from django.contrib import admin
from .models import *
# Register your models here.



class ReviewsInline(admin.TabularInline):
    model = Review
    extra = 1  # Number of extra forms to display


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of extra forms to display

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
    inlines = [ProductImageInline, ReviewsInline]

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SearchQuery._meta.fields]

@admin.register(Amazon_login_Details)
class Amazon_login_DetailsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Amazon_login_Details._meta.fields]

@admin.register(AI_Model)
class AI_ModelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AI_Model._meta.fields]