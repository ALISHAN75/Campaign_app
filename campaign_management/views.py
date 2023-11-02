from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.core import serializers
import time
import threading
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
from campaign_app.utils import get_page_range
import requests
import os
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Q
from .forms import UserForm, ContactsForm, CampaginForm
from .models import Contacts, CampaignSucceedMsgContact, Campaign
import csv
from .utils import MMPhoneNumber
from smtplib import SMTPRecipientsRefused
from django.utils import timezone
from .decorators import redirect_if_logged_in
from django.utils.decorators import method_decorator


class LoginView(View):
    # @method_decorator(redirect_if_logged_in)
    def get(self,request):
        return render(request,'login.html',{})
    
    # @method_decorator(redirect_if_logged_in)
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            success_redirect = request.GET.get('next','/campaign-management/list-contacts')
            login(request, user)
            #request.session.set_expiry(3000)
            return redirect(success_redirect)
        else:
            messages.warning(request, f"Invalid Credentials!")
            return redirect('campaign_management:login')


class LogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('campaign_management:login')
    

def add_user(request):
    if request.method == "GET":
        user_form = UserForm()
        return render(request, 'user_management/add_user.html', {"user_form" : user_form})
    elif request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid() :
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            username = user_form.cleaned_data['username']
            email = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password']
            user_form_data = user_form.save(commit=False)
            user_form_data.set_password(password)
            user_form_data.save()
            message = "{} added successfully!".format(username)
            messages.success(request, message)
            # return redirect(request.path_info)
            return redirect('/campaign-management/login') 
        return render(request, 'user_management/add_user.html', {"user_form" : user_form})



@login_required(login_url="campaign_management:login")
def upload_contacts(request):
    if request.method == "GET":
        form = ContactsForm()
        return render(request, 'add_contact.html', {"form" : form})
    
    elif request.method == 'POST' and request.FILES['fileInput']:
        csv_file = request.FILES['fileInput']
        decoded_file = csv_file.read().decode('utf-8')
        csv_reader = csv.reader(decoded_file.splitlines(), delimiter=',')
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            name, email, phone = row
            Contacts.objects.create(name=name, email=email, phone=phone)
            message = "{} added successfully!".format(form.cleaned_data['name'])
            messages.success(request, message)
            return redirect(request.path_info) 
        return render(request, 'add_contact.html',{"form" : form})
    


@login_required(login_url="campaign_management:login")
def add_contact(request):
    if request.method == "GET":
        form = ContactsForm()
        return render(request, 'add_contact.html', {"form" : form})
        
    elif request.method == 'POST' and 'csv_file' in request.FILES:
        form = ContactsForm()
        csv_file = request.FILES['csv_file']
        mm_phonenumber = MMPhoneNumber()
        # Check if the uploaded file has a CSV extension
        if not csv_file.name.lower().endswith('.csv'):
            messages.warning(request, "Only CSV files are allowed.")
            return render(request, 'add_contact.html', {"form": form})
        decoded_file = csv_file.read().decode('utf-8')
        csv_reader = csv.reader(decoded_file.splitlines(), delimiter=',')
        # Skip the header row
        next(csv_reader)  
        for row in csv_reader:
            name, email, phone, city, address, is_ims_contact, is_advertised_contact  = row
            if not mm_phonenumber.is_valid_mm_phonenumber(phonenumber=phone):
                message = f"{phone} - Invalid Phone Number. Valid format e.g... +959512345678"
                messages.warning(request, message)
                return render(request, 'add_contact.html',{"form" : form})
            else:
                same_email = Contacts.objects.filter(email=email)
                same_phone = Contacts.objects.filter(phone=phone)
                if same_email.exists():
                    messages.warning(request, "{} Contact with this email already exists!.".format(email))
                    return render(request, 'add_contact.html',{"form" : form})
                elif same_phone.exists():
                    messages.warning(request, "{} Contact with this phone number already exists!.".format(phone))
                    return render(request, 'add_contact.html',{"form" : form})
                else:
                    is_ims_contact = is_ims_contact.strip()
                    is_advertised_contact = is_advertised_contact.strip()
                    Contacts.objects.create(
                        name=name, email=email, phone=phone, 
                        city=city, address=address, is_ims_contact=True, is_advertised_contact=is_advertised_contact )
                    message = "Contacts added successfully!"
        messages.success(request, message)
        return redirect(request.path_info) 
        # return render(request, 'add_contact.html',{"form" : form})
    elif request.method == "POST":
        form = ContactsForm(request.POST, request.FILES)
        if form.is_valid():
            saved = form.save()
            message = "{} added successfully!".format(form.cleaned_data['name'])
            messages.success(request, message)
            return redirect(request.path_info) 
        return render(request, 'add_contact.html',{"form" : form})



@login_required(login_url="campaign_management:login")
def list_prev_campaigns(request):
    page_number = request.GET.get('page',1)
    campaigns = Campaign.objects.all().order_by('-id')
    paginator = Paginator(campaigns, 10)
    page_range = get_page_range(1,paginator.num_pages ,int(page_number))
    campaigns_items_paginator = paginator.get_page(page_number)
    return render(request, 'list_prev_campaigns.html',{"campaigns_items_paginator":campaigns_items_paginator, "total_campaigns": len(campaigns),  "page_range" : page_range})



@login_required(login_url="campaign_management:login")
def list_contacts(request):
    page_number = request.GET.get('page',1)
    search_text = request.GET.get('search_text',None)
    contacts = Contacts.objects.all().order_by('-id')
    if search_text:
        contacts = Contacts.objects.filter(Q(name__icontains=search_text) 
                                   | Q(email__icontains=search_text) 
                                   | Q(phone__icontains=search_text) 
                                   | Q(city__icontains=search_text))
    paginator = Paginator(contacts, 10)
    page_range = get_page_range(1,paginator.num_pages ,int(page_number))
    contacts_items_paginator = paginator.get_page(page_number)
    return render(request, 'list_contacts.html',{"contacts_items_paginator":contacts_items_paginator, "total_contacts": len(contacts),  "page_range" : page_range})




@login_required(login_url="user_management:login")
def edit_contact(request, pk):
    instance = Contacts.objects.get(id=pk)
    if request.method == "GET":
        form = ContactsForm(instance=instance)
        return render(request, 'edit_contact.html',{"form":form})
    elif request.method == "POST":
        form = ContactsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            instance.updated_on = timezone.now()
            instance.save()
            message = "{} updated successfully!".format(instance.name)
            messages.success(request, message)
            return redirect(request.path_info) 
        return render(request, 'edit_contact.html',{"form" : form})



@login_required(login_url="user_management:login")
def delete_contact(request, pk):
    try:
        instance = Contacts.objects.get(id=pk)
        instance.delete()
        message = "{} deleted successfully!".format(instance.name)
        messages.success(request, message)
        return redirect('campaign_management:list_contacts')
    except Exception as e:
        message = "{} \n Instance not deleted successfully!".format(e)
        messages.warning(request, message)
        return redirect('campaign_management:list_contacts')




def syncing_clients(request):
    url = "http://207.244.105.191:8866/clients_app/get_company_clients/"
    headers = {
            "API-Secret-Name": "CAMPAIGN APP",
            "API-Secret-Key": "c36317f7-0fe0-40da-b32d-f6beb30367d9",
        }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        data = response.json()
        if response.status_code == 200 and "data" in data and "clients" in data["data"]:
            clients = data["data"]["clients"]
            if not clients:
                messages.success(request, "API response has no client data")
                return redirect('campaign_management:list_contacts')
            else:
                mm_phonenumber = MMPhoneNumber()
                for client in clients:
                    phone_number = client.get("phone")
                        # Add +95 prefix if the phone number doesn't start with it
                    if not phone_number.startswith("+95"):
                        phone_number = "+95" + phone_number
                    if mm_phonenumber.is_valid_mm_phonenumber(phonenumber=phone_number):
                        if Contacts.objects.filter(email=client.get("email")).exists() or Contacts.objects.filter(phone=phone_number).exists():
                            continue
                        else:
                            Contacts.objects.create(
                                    name=client.get("name"),
                                    email=client.get("email"),
                                    phone=phone_number,
                                    city=client.get("city"),
                                    address=client.get("address"),
                                    is_ims_contact=True
                                    )
            messages.success(request, "Contacts Synced Succuessfully!")
            return redirect('campaign_management:list_contacts')
        else:
            messages.warning(request, "No data found in API response")
            return redirect('campaign_management:list_contacts')
    except requests.exceptions.RequestException as e:
        messages.warning(request, f"API request failed: {e}")
        return redirect('campaign_management:list_contacts')
    except (ValueError, KeyError):
        messages.warning(request, "Invalid API response data")
        return redirect('campaign_management:list_contacts')
    except Exception as e:
        messages.warning(request, f"An unexpected error occurred: {e}")
        return redirect('campaign_management:list_contacts')
    

@login_required(login_url="campaign_management:login")
def sync_contacts(request):
    if request.method == "GET":
        thread1 = threading.Thread(target=syncing_clients,  args=(request,))
        thread1.start()
        messages.success(request, "Contacts are syncing in background please wait upto 2-3 minutes.")
        return redirect('campaign_management:list_contacts')

        
# @login_required
def client_search(request):
    response = {}
    keyword = request.GET.get('keyword')
    try:
        clients = []
        clients = Contacts.objects.filter(Q(name__icontains=keyword) | Q(email__icontains=keyword) | Q(phone__icontains=keyword) | Q(city__icontains=keyword)).values('pk', 'name','email','phone','city')
        response['data'] = list(clients)
    except Exception as e:
        response['data'] = []
    return JsonResponse(response)


        

# @login_required(login_url="campaign_management:login")
# def sync_contacts(request):
#     if request.method == "GET":

#         url = "http://207.244.105.191:8866/clients_app/get_company_clients/"
#         headers = {
#             "API-Secret-Name": "CAMPAIGN APP",
#             "API-Secret-Key": "c36317f7-0fe0-40da-b32d-f6beb30367d9",
#         }
#         try:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
#             data = response.json()
#             if response.status_code == 200 and "data" in data and "clients" in data["data"]:
#                 clients = data["data"]["clients"]
#                 if not clients:
#                     messages.success(request, "API response has no client data")
#                     return redirect('campaign_management:list_contacts')
#                 else:
#                     mm_phonenumber = MMPhoneNumber()
#                     for client in clients:
#                         phone_number = client.get("phone")
#                         # Add +95 prefix if the phone number doesn't start with it
#                         if not phone_number.startswith("+95"):
#                             phone_number = "+95" + phone_number
#                         if mm_phonenumber.is_valid_mm_phonenumber(phonenumber=phone_number):
#                             if Contacts.objects.filter(email=client.get("email")).exists() or Contacts.objects.filter(phone=phone_number).exists():
#                                 continue
#                             else:
#                                 Contacts.objects.create(
#                                     name=client.get("name"),
#                                     email=client.get("email"),
#                                     phone=phone_number,
#                                     city=client.get("city"),
#                                     address=client.get("address"),
#                                     is_ims_contact=True
#                                     )
                                

#                 messages.success(request, "Contacts Synced Succuessfully!")
#                 return redirect('campaign_management:list_contacts')
#             else:
#                 messages.warning(request, "No data found in API response")
#                 return redirect('campaign_management:list_contacts')
#         except requests.exceptions.RequestException as e:
#             messages.warning(request, f"API request failed: {e}")
#             return redirect('campaign_management:list_contacts')
#         except (ValueError, KeyError):
#             messages.warning(request, "Invalid API response data")
#             return redirect('campaign_management:list_contacts')
#         except Exception as e:
#             messages.warning(request, f"An unexpected error occurred: {e}")
#             return redirect('campaign_management:list_contacts')






@login_required(login_url="campaign_management:login")
def add_campaign(request):
    if request.method == "GET":
        form = CampaginForm()
        cities = Contacts.objects.values_list("city", flat=True).distinct().order_by("city")
        contacts = Contacts.objects.all()
        # html_data = ''
        # for contact in contacts:
        #     html_data += f"""<div class="is-load-list">
        #          <label><input type="checkbox" value="{contact.id}"> {contact.name } - {contact.email} </label><br>
        #     </div>"""
        #     # html_data += f"""<div class="is-load-list">
        #     #      <option value="{contact.id}">{contact.name } - {contact.email}</option>
        #     # </div>"""
        # # Open the file in write mode, truncating previous data
        # with open('static/client.html','w', errors='replace', encoding='utf-8') as file:
        #     file.write(html_data)

        return render(request, 'add_campaign.html', {"form": form, "cities": cities, "contacts": contacts, })
    

    elif request.method == "POST":
        form = CampaginForm(request.POST, request.FILES)
        if form.is_valid() :
            TESING_MOBILE_NUMBER = os.getenv('TESING_MOBILE_NUMBER')
            ENVIRONMENT = os.getenv('ENVIRONMENT')
            name = form.cleaned_data['name']
            datetime_field = form.cleaned_data['datetime_field']
            message_type = form.cleaned_data['type']
            schedule_campaign = form.cleaned_data['schedule_campaign']
            choice_type = form.cleaned_data['clients']
            # email_subject = form.cleaned_data['email_subject']
            email_subject = form.cleaned_data.get('email_subject', " ")
            email_text = form.cleaned_data.get('email_text_editor', " ")
            sms_text = form.cleaned_data.get('sms_text_area', " ")
            select_clients = request.POST.getlist('select_clients', [])
            select_cities = request.POST.getlist('select_cities', [])
            recipients = []
            if choice_type == "All Clients":
                recipients = Contacts.objects.all()
            elif choice_type == "Select Cities" and len(select_cities)>0:
                recipients = Contacts.objects.filter(city__in=select_cities)
            elif choice_type == "Select Clients" and len(select_clients)>0:
                recipients = Contacts.objects.filter(id__in=select_clients)
            elif choice_type == "All Advertised Clients":
                recipients = Contacts.objects.filter(is_advertised_contact=True)
            elif choice_type == "All IMS Clients" :
                recipients = Contacts.objects.filter(is_ims_contact=True)
            else:
                messages.warning(request, "Please Select Clients")
                return redirect(request.path_info)
            # Send emails to the selected recipients
            if schedule_campaign == "Select DateTime" and len(recipients)>0:
                # new_campaign = form.save()
                # current_dt = datetime.now()
                campaign_obj = Campaign.objects.create(name=name, type=message_type,email_subject = email_subject,
                                                      email_body=email_text, sms_body=sms_text, campaign_datetime=datetime_field, status = "DUE" )
                campaign_obj.contacts.add(*recipients)
                # for recipient in recipients:
                #     CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign_obj)            
                if campaign_obj:
                    # Display success message
                    messages.info(request, "Campaign messages scheduled successfully!")  
                else:
                    # Display error message
                    messages.error(request, "Failed to schedule campaign messages.")  
            elif schedule_campaign == "Now"  and len(recipients)>0:
                current_dt = datetime.now()
                campaign_obj = Campaign.objects.create(name=name, type=message_type,email_subject = email_subject,
                                                      email_body=email_text, sms_body=sms_text, campaign_datetime=current_dt, status ="SENT" )
                campaign_obj.contacts.add(*recipients)
                for recipient in recipients:
                    if message_type == 'Email':
                        # Sanitize and clean the HTML content
                        try:
                            # Use render_to_string to render the HTML email content
                            html_content = render_to_string('email_template.html', {'recipient_name': recipient.name, 'email_text': email_text})
                            # Use EmailMessage to send the HTML email
                            msg = EmailMessage(
                                subject=email_subject,
                                body=html_content,
                                from_email=settings.EMAIL_HOST_USER,
                                to=[recipient.email],
                            )
                            msg.content_subtype = 'html'  # Set the content type to HTML
                            msg.send()
                            recipient.status = "SUCCESS"
                            recipient.save()
                            CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign_obj)            
                        except SMTPRecipientsRefused as e:
                            # Handle the exception here and print the invalid email address
                            recipient.status = "FAILED"
                            recipient.save()
                            CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign_obj)            
                            # messages.warning(request,f"Invalid email address: {recipient.email}")
                            # return redirect(request.path_info)
                        except Exception as e:
                            # Handle other exceptions here
                            recipient.status = "FAILED"
                            recipient.save()
                            CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign_obj)            
                    elif message_type == 'SMS':
                        # Loop through recipients and send SMS
                        mobile_num = ''
                        if ENVIRONMENT == "development":
                            mobile_num = TESING_MOBILE_NUMBER
                        else:
                            mobile_num = recipient.phone
                        try:
                            # Prepare SMS data
                            sms_body_text = campaign_obj.sms_body
                            if "{client_name}" in sms_body_text:
                                sms_body_text = sms_body_text.replace("{client_name}", recipient.name)
                            if "{client_phoneNumber}" in sms_body_text:
                                sms_body_text = sms_body_text.replace("{client_phoneNumber}", recipient.phone)
                            if "{client_email}" in sms_body_text:
                                sms_body_text = sms_body_text.replace("{client_email}", recipient.email)
                            sms_data = {
                                    "mobile_numbers": [mobile_num],
                                    "message": sms_body_text,
                                }
                                # Send SMS using the API
                            # api_url = "http://207.244.105.191:8866/clients_app/send_campaign_sms/"
                            api_url = "http://207.244.105.191:8866/clients_app/jzbc/"
                            headers = {
                                    "API-Secret-Name": "CAMPAIGN APP",
                                    "API-Secret-Key": "c36317f7-0fe0-40da-b32d-f6beb30367d9",
                                }
                            response = requests.post(api_url, json=sms_data, headers=headers)
                                # Check if SMS was sent successfully
                            if response.status_code == 200:
                                transaction_id = response.json().get("data", {}).get("transaction_id")
                                # Send transaction ID to another API for details
                                while True:
                                    transaction_details_url = "http://207.244.105.191:8866/clients_app/campaign_sms_transaction_details/"
                                    transaction_details_data = {
                                            "transaction_id": transaction_id,
                                        }
                                    # print("transaction_id", transaction_id)
                                    # print("mobile_num", mobile_num)
                                    # print("sms_body_text", sms_body_text)
                                    headers = {
                                        "API-Secret-Name": "CAMPAIGN APP",
                                        "API-Secret-Key": "c36317f7-0fe0-40da-b32d-f6beb30367d9",
                                        }
                                    transaction_response = requests.post(transaction_details_url, json=transaction_details_data, headers=headers)
                                    if transaction_response.status_code == 200:
                                        final_status = transaction_response.json().get("data", {}).get("content", [])[0].get("finalStatus")
                                        if final_status != "PROCESS":
                                            if final_status == "DELIVRD":
                                                recipient.status = "SUCCESS"
                                            else:
                                                recipient.status = "FAILED"
                                                # print("1")
                                            break
                                        # print("final_status", final_status)
                                    else:
                                        recipient.status = "FAILED"
                                        # print("2")
                            else:
                                recipient.status = "FAILED"
                                # print("3")
                            # Save recipient status
                            recipient.save()
                            CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign_obj)            
                        except Exception as e:
                            recipient.status = "FAILED"
                            # print("4")
                            recipient.save()
                            CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign_obj)            


                    # Existing code below ...
                
                messages.success(request, "Campaign messages sent successfully!")
                return redirect(request.path_info)
            else:
                messages.success(request, "Select Schedule Campaign!")
                return redirect(request.path_info)
                # if campaigns.exists():
                    # for campaign in campaigns:
                        # print("Campaign:", campaign.name)
                        # print("email_subject:", campaign.email_subject)
                        # print("email_body:", campaign.email_body)
                        # print("sms_body:", campaign.sms_body)
                        # print("campaign_datetime:", campaign.campaign_datetime)
                        # for contact in campaign.contacts.all():
                        #     print("Contact:", contact.name, "-", contact.email)
                # recipient_ids = [id for id in recipients]
                #  Schedule the email sending task
                # success = schedule_email_sending(campaign_id, datetime_field, recipient_ids, email_subject, email_text) 
            
            
            
            return redirect('campaign_management:add_campaign')
        cities = Contacts.objects.values_list("city", flat=True).distinct().order_by("city")
        contacts = Contacts.objects.all()
        return render(request, 'add_campaign.html', {"form": form, "cities": cities, "contacts": contacts})






@login_required(login_url="campaign_management:login")
def list_campaigns(request):
    campaigns = Campaign.objects.all().order_by('-id')  # Get all campaigns to populate the dropdown
    selected_campaign_id = request.GET.get('campaign', '')  # Get the selected campaign ID from the query parameter

    # Filter contacts based on the selected campaign
    campaign_msgs = CampaignSucceedMsgContact.objects.all().order_by('-id')
    if selected_campaign_id:
        campaign_msgs = campaign_msgs.filter(campaign_id=selected_campaign_id)
    paginator = Paginator(campaign_msgs, 10)
    page_number = request.GET.get('page', 1)
    page_range = get_page_range(1, paginator.num_pages, int(page_number))
    campaign_msgs_items_paginator = paginator.get_page(page_number)

    return render(request, 'list_campaign.html', {
        "campaigns": campaigns,
        "selected_campaign_id": selected_campaign_id,
        "campaign_msgs_items_paginator": campaign_msgs_items_paginator,
        "page_range": page_range
    })



