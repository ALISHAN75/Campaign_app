from django.urls import path
from .views import *
from django.utils.decorators import method_decorator
from .decorators import redirect_if_logged_in
app_name = "campaign_management"

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('logout',LogoutView.as_view(),name="logout"),   
    # path('sign-up/', add_user, name="sign_up" ),

    path('list-contacts/', list_contacts, name="list_contacts"),
    path('add-contact/', add_contact, name="add_contact"),
    path('edit-contact/pk=<int:pk>', edit_contact , name="edit_contact"),
    path('delete-contact/pk=<int:pk>', delete_contact , name="delete_contact"),
    path('sync-contacts/', sync_contacts, name='sync_contacts'),
    path('add-campaign/', add_campaign, name="add_campaign"),
    path('list-campaign/', list_campaigns, name="list_campaigns"),

    path('list-prev-campaigns/', list_prev_campaigns, name="list_prev_campaigns"),

    path('client-search/', client_search, name="client_search"),

] 