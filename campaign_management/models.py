from django.db import models
from tinymce.models import HTMLField


# Create your models here.

class Contacts(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True )
    email = models.EmailField(max_length=56, unique=True, null=False, blank=False)
    phone = models.CharField(max_length=56,  unique=True, null=False, blank=False)
    city = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    is_ims_contact = models.BooleanField(default=False)
    is_advertised_contact = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(null=True, blank=True, max_length=12, choices=(('FAILED', 'FAILED'),('SUCCESS', 'SUCCESS' )))
    
    class Meta:
        verbose_name = 'contact'
        verbose_name_plural = 'contacts'

    def __str__(self):
        return '{}-{}'.format(self.name, self.email)
    

class Campaign(models.Model):
    name = models.CharField(max_length=32, null=True, blank=True )
    type = models.CharField(null=False, blank=False, max_length=12, choices=(('SMS', 'SMS'),('Email', 'Email')))
    contacts = models.ManyToManyField(Contacts, related_name="campaign_contacts", blank=True)
    email_subject = models.CharField(max_length=1024, null=True, blank=True)
    email_body = HTMLField()
    sms_body = models.TextField(max_length=1024,null=True, blank=True)
    campaign_datetime = models.DateTimeField(null=True, blank=True)
    status = models.CharField(null=True, blank=True, max_length=12, choices=(('DUE', 'DUE'), ('SENT', 'SENT' )))
    
    class Meta:
        verbose_name = 'campaign'
        verbose_name_plural = 'campaigns'

    def __str__(self):
        return '{}-{}'.format(self.name, self.campaign_datetime)
    

class CampaignSucceedMsgContact(models.Model):
    contacts = models.ForeignKey(Contacts, null=True, blank=True, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'campaignsucceedmsgcontact'
        verbose_name_plural = 'campaignsucceedmsgcontacts'

    def __str__(self):
        return '{}-{}'.format(self.contacts, self.campaign)