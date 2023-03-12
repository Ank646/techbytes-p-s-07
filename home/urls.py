from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),

    path("college", views.college, name="college"),
    path("login", views.login, name="login"),
    path("myregev", views.myregev, name="myregev"),

    path("logincollege", views.logincollege, name="logincollege"),
    path("signupcollege", views.signupcollege, name="signupcollege"),
    path("signup", views.signup, name="signup"),
    path("collegeevent/<str:colleve>", views.collegeevent, name="collegeevent"),

    path("contact", views.contact, name="contact"),
    path("logout", views.logout, name="logout"),
    path("logoutcollege", views.logoutcollege, name="logout"),
    path("registerevent", views.registerevent, name="registerevent"),
    path("eventpage/<str:id>", views.eventpage, name="eventpage"),
    path("partevent/<str:id>", views.partevent, name="partevent"),
    path("cancelregistration/<str:id>",
         views.cancelregistration, name="cancelregistration"),

    path("participants/<str:evuu>", views.participants, name="participants"),

    path("search", views.search, name="search")
]
