from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
from django.contrib.auth.models import User
from .models import Contacts, Campaign
from .utils import MMPhoneNumber
from datetime import datetime
from django.utils import timezone
# from tinymce.models import HTMLField
# from tinymce.widgets import TinyMCE

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username","first_name","last_name","email","password"]

        widgets = {
            'username': forms.TextInput(attrs={'required': True}, ),
            'password': forms.PasswordInput(attrs={'required': True}, ),
        }

        labels = {
            "username" : "User name",
            "password" : "Password",
        }



class ContactsForm(forms.ModelForm):
    class Meta:
        model = Contacts
        # fields = "__all__"
        fields = ("name", "email", "phone", "city", "address", "is_ims_contact", "is_advertised_contact")

        widgets = {
            'email': forms.TextInput(attrs={'required': True},),
            'phone': forms.TextInput(attrs={'required': True},),
            'status': forms.TextInput(attrs={'required': False},),
        }

        labels = {
            "name": "Name",
            "email" : "Email",
            "phone" : "Phone Number",
            "address" : "Address",
        }
    

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        instance = self.instance
        mm_phonenumber = MMPhoneNumber()
        if not instance.pk:  
            if not mm_phonenumber.is_valid_mm_phonenumber(phonenumber=phone):
                # Show Error Message
                self.add_error('phone', 'Invalid Phone Number. Valid format e.g... +959512345678')
            if Contacts.objects.filter(email=email).exists():
                self.add_error('email', 'Contact with this email already exists')
            if Contacts.objects.filter(phone=phone).exists():
                self.add_error('phone', 'Contact with this Phone Number already exists')
        else:
            if not mm_phonenumber.is_valid_mm_phonenumber(phonenumber=phone):
                # Show Error Message
                self.add_error('phone', 'Invalid Phone Number. Valid format e.g... +959512345678')
            if Contacts.objects.filter(email=email).exclude(pk=instance.pk).exists():
                self.add_error('email', 'Contact with this email already exists')
            if Contacts.objects.filter(phone=phone).exclude(pk=instance.pk).exists():
                self.add_error('phone', 'Contact with this Phone Number already exists')
            # instance.updated_on = datetime.now
            # instance.save()

        return cleaned_data

        


# class CampaginForm(forms.ModelForm):
#     class Meta:
#         model = Campaign
#         fields = ( "name", "message","type")

#         widgets = {
#             'name': forms.TextInput(attrs={'placeholder': 'Enter Name'}),
#             'message': forms.TextInput(attrs={'placeholder': 'Enter Message'}),
#         }

#         labels = {
#             "name": "Camp Name",
#             "message" : "Message",
#             "type" : "Type",

#         }


# class ContactsMultipleChoiceField(forms.ModelMultipleChoiceField):
#     def label_from_instance(self, obj):
#         return f"{obj.name}-{obj.email}-{obj.phone}"
    
# class CampaginForm(forms.ModelForm):
#     email_subject = forms.CharField(
#         label="Subject", widget=forms.TextInput(attrs={'placeholder': 'Enter Subject'}),
#         required=False  # Set required to False
#     )
#     email_text_editor = forms.CharField(
#         label="Text Editor", widget=AdminTextareaWidget(),
#         required=False  # Set required to False
#     )
#     sms_text_area = forms.CharField(
#         label="SMS Message", widget=AdminTextareaWidget(),
#         required=False  # Set required to False
#     )
#     datetime_field = forms.DateTimeField(
#         label="Select DateTime", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
#     )
#     select_clients = ContactsMultipleChoiceField(
#         queryset=Contacts.objects.all(),
#         widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
#         required=False
#     )
    

#     class Meta:
#         model = Campaign
#         fields = ("name", "type")
#         widgets = {
#             'name': forms.TextInput(attrs={'placeholder': 'Enter Name'}),
#             'type': forms.Select(attrs={'onchange': 'toggleFields()'}),
#         }

#         labels = {
#             "name": "Campaign Name",
#             "type": "Type",
#         }



# class ContactsMultipleChoiceField(forms.ModelMultipleChoiceField):
#     def label_from_instance(self, obj):
#         return f"{obj.name}-{obj.email}-{obj.phone}"

# def get_cities_from_backend():
#     # Retrieve distinct cities from the Contacts model
#     return Contacts.objects.values_list('city', flat=True).distinct()

class CampaginForm(forms.ModelForm):
    email_subject = forms.CharField(
        label="Subject", widget=forms.TextInput(attrs={'placeholder': 'Enter Subject'}),
        required=False  # Set required to False
    )
    email_text_editor = forms.CharField(
        label="Email Body", widget=AdminTextareaWidget(),
        required=False  # Set required to False
    )
    sms_text_area = forms.CharField(
        label="SMS Message", widget=AdminTextareaWidget(attrs={'placeholder': "Dear {client_name}, ..."}),
        required=False  # Set required to False
    )
    # datetime_field = forms.DateTimeField(
    #     label="Select DateTime", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    #     required=False  # Set required to False
    # )
    datetime_field = forms.DateTimeField(
    label="Select DateTime",
    widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'min': timezone.now().strftime('%Y-%m-%dT%H:%M')}),
    required=False
    )

    schedule_campaign = forms.ChoiceField(
        label="Schedule Campaign",
        choices=(('-------', '-------'),('Now', 'Now'), ('Select DateTime', 'Select DateTime')),
        required=True  # Set required to False if you want the field to be optional
    )
    clients = forms.ChoiceField(
        label="Clients",
        choices=(('-------', '-------'), ('All Clients', 'All Clients'), ('All Advertised Clients', 'All Advertised Clients'), ('All IMS Clients', 'All IMS Clients'),  ('Select Clients', 'Select Clients'), ('Select Cities', 'Select Cities')),
        required=True  # Set required to False if you want the field to be optional
    )
    
    class Meta:
        model = Campaign
        fields = ("name", "type" )
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter Name'}),
            'type': forms.Select(attrs={'onchange': 'toggleFields()'}),
            'clients': forms.Select(attrs={'onchange': 'toggleForms()'}),
            'schedule_campaign': forms.Select(attrs={'onchange': 'toggleCampaign()'}),
        }

        labels = {
            "name": "Campaign Name",
            "type": "Type",
        }
