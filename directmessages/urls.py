from django.urls import path
from directmessages import views


urlpatterns = [
    path("inbox", views.inbox, name="inbox"),
    path("messages/<username>", views.Directs, name="direct"),
    path("send", views.SendDirect, name="send"),
    path("send/<username>", views.NewMessage, name="new-message"),
    path("search", views.userSearch, name="search"),
]
