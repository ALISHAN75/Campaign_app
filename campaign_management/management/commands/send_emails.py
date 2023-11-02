# myapp/management/commands/send_emails.py
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from campaign_management.models import Campaign, Contacts, CampaignSucceedMsgContact
from django.conf import settings
from datetime import datetime
from django.utils import timezone
import os
import requests
from smtplib import SMTPRecipientsRefused

class Command(BaseCommand):
    help = 'Send scheduled emails for a campaign'
    def handle(self, *args, **options):
        TESING_MOBILE_NUMBER = os.getenv('TESING_MOBILE_NUMBER')
        ENVIRONMENT = os.getenv('ENVIRONMENT')
        # print("Testing")
        # print(TESING_MOBILE_NUMBER)
        # print(ENVIRONMENT)

        try:
            current_dt = datetime.now()
            year = current_dt.year
            month = current_dt.month
            day = current_dt.day
            hour = current_dt.hour
            minute = current_dt.minute

            campaigns = Campaign.objects.filter(
            campaign_datetime__year=year,
            campaign_datetime__month=month,
            campaign_datetime__day=day,
            campaign_datetime__hour=hour,
            campaign_datetime__minute=minute,
            status = "DUE")

            if campaigns.exists():
                for campaign in campaigns:
                    # print("Campaign:", campaign.name)
                    # print("email_subject:", campaign.email_subject)
                    # print("email_body:", campaign.email_body)
                    for recipient in campaign.contacts.all():
                        if campaign.type == "Email":
                        # Sanitize and clean the HTML content
                            try:
                                # Use render_to_string to render the HTML email content
                                html_content = render_to_string('email_template.html', {'recipient_name': recipient.name, 'email_text': campaign.email_body})
                                # Use EmailMessage to send the HTML email
                                msg = EmailMessage(
                                    subject=campaign.email_subject,
                                    body=html_content,
                                    from_email=settings.EMAIL_HOST_USER,
                                    to=[recipient.email],
                                )
                                msg.content_subtype = 'html'  # Set the content type to HTML
                                msg.send()
                                recipient.status = "SUCCESS"
                                recipient.save()
                                CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign)            
                            except SMTPRecipientsRefused as e:
                                # Handle the exception here and print the invalid email address
                                recipient.status = "FAILED"
                                recipient.save()
                                CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign)            
                                print(f"An error occurred :{e}.")
                                # messages.warning(request,f"Invalid email address: {recipient.email}")
                                # return redirect(request.path_info)
                            except Exception as e:
                                # Handle other exceptions here
                                recipient.status = "FAILED"
                                recipient.save()
                                CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign)            
                                print(f"An error occurred :{e}.")
                                # return redirect(request.path_info)
                   
                        elif  campaign.type == "SMS":
                            # Loop through recipients and send SMS
                            if ENVIRONMENT == "development":
                                mobile_num = TESING_MOBILE_NUMBER
                            else:
                                mobile_num = recipient.phone
                            try:
                                # Prepare SMS data
                                sms_body_text = campaign.sms_body
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
                                api_url = "http://207.244.105.191:8866/clients_app/send_campaign_sms/"
                                headers = {
                                        "API-Secret-Name": "CAMPAIGN APP",
                                        "API-Secret-Key": "c36317f7-0fe0-40da-b32d-f6beb30367d9",
                                    }
                                response = requests.post(api_url, json=sms_data, headers=headers)
                                    # Check if SMS was sent successfully
                                if response.status_code == 200:
                                    transaction_id = response.json().get("data", {}).get("transaction_id")
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
                                CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign)            
                            except Exception as e:
                                recipient.status = "FAILED"
                                # print("4")
                                recipient.save()
                                CampaignSucceedMsgContact.objects.create(contacts=recipient, campaign=campaign)            
                                print(f"An error occurred :{e}.")
                    campaign.status = "SENT"
                    campaign.save()
        except Exception as e:
            self.stdout.write(self.style.ERROR('Error {}'.format(e)))











                    # Existing code below ...

                    #     # print("Contact:", contact.name, "-", contact.email)
                    #     if campaign.type == "Email":
                    #         try:
                    #             html_content = render_to_string('email_template.html', {'recipient_name': contact.name, 'email_text': campaign.email_body})
                    #             msg = EmailMessage(
                    #                 subject=campaign.email_subject,
                    #                 body=html_content,
                    #                 from_email=settings.EMAIL_HOST_USER,
                    #                 to=[contact.email],
                    #             )
                    #             msg.content_subtype = 'html'
                    #             msg.send()
                    #             campaign.status = "RUNNING"
                    #             campaign.save()
                    #         except Exception as e:
                    #             print(f"An error occurred: {e}")
                    #     elif campaign.type == "SMS":
                    #         if ENVIRONMENT == "development":
                    #             mobile_num = TESING_MOBILE_NUMBER
                    #         else:
                    #             mobile_num = contact.phone
                    #         try:
                    #             sms_payload = {
                    #                 "mobile_numbers": [mobile_num],
                    #                 "message": campaign.sms_body
                    #             }
                    #             headers = {
                    #                 "API-Secret-Name": "CAMPAIGN APP",
                    #                 "API-Secret-Key": "c36317f7-0fe0-40da-b32d-f6beb30367d9",
                    #             }
                    #             response = requests.post("http://207.244.105.191:8866/clients_app/send_campaign_sms/", json=sms_payload, headers=headers)
                    #             if response.status_code == 200:
                    #                 print("SMS sent successfully.")
                    #                 campaign.status = "RUNNING"
                    #                 campaign.save()
                    #             else:
                    #                 print(f"Failed to send SMS. Status code: {response.status_code}")
                    #         except Exception as e:
                    #             print(f"An error occurred: {e}")
                    #             # Handle the error as needed
                    #         # campaign.status = "RUNNING"
                    #         # campaign.save()
                    # campaign.status = "SENT"
                    # campaign.save()


