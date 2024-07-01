from django.shortcuts import get_object_or_404
from django.contrib import messages
import os
import re
import time
from cmath import exp
from bs4 import BeautifulSoup
from decimal import *
from http.client import EXPECTATION_FAILED
from multiprocessing import context
from urllib import request
import datetime
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.db.models import Avg, Count, Max, Min
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import URLPattern, reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers import serialize
from urllib.parse import urlparse
from .views import *
import re
from django.utils.dateparse import parse_date
# import chromedriver_binary
from .models import *
from django.http import request
import demoji
import threading
from playwright.async_api import async_playwright
from PIL import Image
import pytesseract
import asyncio
from asgiref.sync import sync_to_async
import requests

@sync_to_async
def create_product(title,  link,price_text, product_no):
    Product.objects.create(name=title, link=link,price=price_text, product_no=product_no)


@sync_to_async
def save_product_price(product_no,price_number):
    ab = Product.objects.get(product_no=product_no)
    ab.price = str(price_number)
    ab.save()
    print(ab)
    print(price_number)
    print(price_number)
    

@sync_to_async
def create_review(product_no, buyer_name, review_date, review_rating, review_text, review_title=None, verified_purchase=False):

    product = Product.objects.get(product_no=product_no)
    review = Review(
        product=product,
        buyer_name=buyer_name,
        review_time=review_date,
        review_rating=review_rating,
        review_text=review_text,
        review_title=review_title,
        verified_purchase=verified_purchase
    )
    review.save()

@sync_to_async
def create_product_image(product_no, link_href):
    ProductImage.objects.create(product_id=product_no, image=link_href)





# Function to decode CAPTCHA image windows local and linx server
@sync_to_async
# def decode_captcha(image_url):
#     if not image_url.startswith('http'):
#         image_url = 'https:' + image_url
#     # Download the image
#     with open('captcha_image.jpg', 'wb') as f:
#         response = requests.get(image_url)
#         f.write(response.content)
#     pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
#     # Open and process the image
#     captcha_image = Image.open('captcha_image.jpg')
#     captcha_text = pytesseract.image_to_string(captcha_image)
#     captcha_text = captcha_text.upper().replace(" ", "")
#     return captcha_text
def decode_captcha(image_url):
    # Download the image
    with open('captcha_image.jpg', 'wb') as f:
        response = requests.get(image_url)
        f.write(response.content)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # Open and process the image
    captcha_image = Image.open('captcha_image.jpg')
    captcha_text = pytesseract.image_to_string(captcha_image)
    return captcha_text


async def amazon_api(x,user):
    print('threading start')
    try:
        # Attempt to retrieve an existing record with the same query
        search_query = await sync_to_async(SearchQuery.objects.get)(query=x)
        return JsonResponse({'url': x, 'status': 'Searching'})
    except SearchQuery.DoesNotExist:
        # If no existing record is found, create a new one
        search_query = SearchQuery(query=x, status='Searching')
        await sync_to_async(search_query.save)()
        print('Data created')
    except IntegrityError as e:
        return JsonResponse({'url': x, 'status': str(e)})
    # for proxy in proxy_list:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            screenshot_counter = 1
            while True:
                response = await page.goto(x)
                time.sleep(.3)
                if response.status == 200:
                    html_content = await page.content()
                    screenshot_filename = f'screenshot_load_{screenshot_counter}.png'
                    await page.screenshot(path=screenshot_filename)
                    captcha_image_url_element = await page.query_selector('img')
                    captcha_image_url = await captcha_image_url_element.get_attribute('src')
                    captcha_text = await decode_captcha(captcha_image_url)
                    print("Decoded CAPTCHA:", captcha_text)
                    
                    # Fill input box with CAPTCHA text
                    await page.fill('#captchacharacters', captcha_text)
                    
                    screenshot_filename = f'screenshot_{screenshot_counter}.png'
                    await page.screenshot(path=screenshot_filename)
                    screenshot_counter += 1 
                    
                    # Submit the form
                    await page.click('button[type="submit"]')
                    # await page.wait_for_navigation()
                    # Check if CAPTCHA is still present
                    if await page.query_selector('#captchacharacters'):
                        continue  # Continue solving CAPTCHA if it's still present
                    else:
                        print("No more CAPTCHA found. Exiting loop.")
                        break  # Exit loop if no more CAPTCHA found
                else:
                    print(f"Request failed with status code {response.status}")
                    break  # Exit loop if request fails
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            await page.wait_for_load_state()
            html_content = await page.content()
    # Use BeautifulSoup to parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Continue with the rest of your code for scraping and processing
            product_data = dict()
            kkas = uuid.uuid4().hex[:5].upper()
            product_data['no'] = kkas
            kls = product_data['no']
            # Example: Extracting the title
            title_element = soup.find(id='title') or soup.find(id='truncatedTitle')
            if title_element:
                titlel = title_element.text.replace("/", " ").replace("%", " ").replace(" \ ", " ").replace(" | ", " ")
                import re
                title =  titlel
            else:
                title = "Title not found"
            print(title)
            product_data['title'] = title
            
            q = x
            l = q
            newurl = l
            price = False
            price_text = 0
            if price == False:
                price_element = soup.find(class_='a-offscreen')
                p='Quantity'
                color=None
                if price_element:
                    price_text = price_element.text.replace('$', '')
                    
                    if price_text.replace('.', '', 1).isdigit():
                        # If the text represents a number, convert and print the number
                        price_number = float(price_text)
                        # await create_sku_size(kls, color,p, price_number)
                        print(f"Size: Quantity, Price: {price_number}")
                        price_text = price_number

                    else:
                        # Find the script tag containing "dimensionValuesDisplayData"
                        price_elements = soup.find(class_='reinventPricePriceToPayMargin priceToPay')
                        if price_element:
                            price_element = price_elements.find(class_='a-offscreen')
                            price_text = price_element.text.replace('$', '')
                            if price_text.replace('.', '', 1).isdigit():
                                # If the text represents a number, convert and print the number
                                price_number = float(price_text)
                                # await create_sku_size(kls, color,p, price_number)
                                print(f"Size: Quantity, Price: {price_number}")
                                price_text = price_number
                            else:
                                # If the text is not a number, print the text
                                print("Text:", price_text)
                                price_text = price_text
                                # price_text = 'Stock Out'                    
                                # await create_sku_size(kls, color,p, price_text)
                        else:
                            price_text = 'Stock Out'                    
                            # await create_sku_size(kls, color,p, price_text)
              
            await create_product(product_data['title'],newurl,price_text, product_data['no'])
            
            
            
            
            # Example: Extracting images
            images = soup.find(id='lookbook_content_div') or soup.find(id='image-block') or soup.find(id='altImages')

            if images:
                img_tags = images.find_all('img')
                for img in img_tags:
                    if 'gif' not in img.get('src') and '360_icon' not in img.get('src') and 'PKdp-play-icon-overlay_' not in img.get('src'):
                        link_href = img.get('src').replace('._AC_UF894,1000_QL80_FMwebp_','').replace('_AC_SR38,50_.','').replace('._AC_US40_','').replace('._AC_US100_','').replace('._SX342_SY445_','').replace('._AC_SY300_SX300_','').replace('L.__AC_SX300_SY300_QL70_ML2_','').replace('._SS40_','').replace('._SX342_SY445_','').replace('._SX38_SY50_CR,0,0,38,50_','').replace('._SX300_SY300_QL70_ML2_','')
                        # Process the image link as needed
                        print(link_href)
                        await create_product_image(product_data['no'], link_href)
               
            # Continue with the rest of your code...
           
            # Click the last "See all reviews" button
            all_review_buttons = await page.query_selector_all('[data-hook="see-all-reviews-link-foot"]')
            if all_review_buttons:
                await all_review_buttons[-1].click()
                await page.wait_for_load_state('domcontentloaded')

            total_reviews = 0
            while total_reviews < 4000:
                try:
                    html_content = await page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')

                    review_section = soup.find(id='cm_cr-review_list')
                    reviews = review_section.find_all(attrs={'data-hook': 'review'})

                    for review in reviews:
                        customer_name = review.find(class_='a-profile-name').get_text()
                        text_without_emoji = demoji.replace(customer_name, "")

                        rating = review.find(class_='a-icon-alt').text
                        rev_date = review.find(class_='review-date').text
                        review_date = parse_date(rev_date)  # Parse date to standard format

                        rev_text = review.find(class_='review-text').text
                        text_without_emoji_rev = demoji.replace(rev_text, "")

                        review_title = review.find(attrs={'data-hook': 'review-title'}).text if review.find(attrs={'data-hook': 'review-title'}) else None
                        verified_purchase = True if review.find(attrs={'data-hook': 'avp-badge'}) else False

                        print(f'Customer Name: {text_without_emoji}, Rating: {rating}, Review Date: {review_date}, Review Text: {text_without_emoji_rev}, Review Title: {review_title}, Verified Purchase: {verified_purchase}')
                        
                        await create_review(product_data['no'], text_without_emoji, review_date, rating, text_without_emoji_rev, review_title, verified_purchase)

                        total_reviews += 1

                    # Check for the "Next page" button
                    next_button = soup.select_one('li.a-last a')
                    if not next_button or 'a-disabled' in next_button.parent.get('class', []):
                        print("No more pages to scrape.")
                        break

                    await page.click('li.a-last a')
                    await page.wait_for_timeout(2000)  # Adjust the timeout as needed
                except:
                    email = ''
                    password = ''
                    await login(page, email, password)
            product = await sync_to_async(Product.objects.get)(product_no=product_data['no'])  
            search_query.user_id = user
            search_query.product = product
            search_query.status = 'Completed'
            await sync_to_async(search_query.save)()
            await browser.close()
    # Example: Creating Product object
    # Replace the following line with the appropriate logic for your project
    # Product.objects.create(name=title, link=x, product_no=search_query.query)

    # Return the response
    return { 'status': 'Success'}




async def login(page, email, password):
    abs = await asyncio.to_thread(Amazon_login_Details.objects.last)
    # Fill email and submit
    await page.fill('#ap_email', abs.email)
    await page.press('#ap_email', 'Enter')

    # Wait for the password field to be visible
    await page.wait_for_selector('#ap_password', timeout=10000)  # Adjust timeout as needed
    await asyncio.sleep(3)

    # Fill password and submit
    await page.fill('#ap_password', abs.password)
    await page.press('#ap_password', 'Enter')

    # Wait for the page to reload after login
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(4)