"""
URL configuration for wad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from setsearch.views import *

urlpatterns = [
    # SetSearch
    path("", home_page, name="home"),
    path("profile", profile, name="profile"),
    path("upcoming", upcoming_concerts, name="upcoming"),

    # artists
    path("artists/<str:artist_slug>", view_artist, name="artist"),

    # concerts
    path("concerts/create", create_concert, name="concert_create"),
    path("artists/<str:artist_slug>/concerts/<str:concert_slug>", view_concert, name="concert"),
    path("artists/<str:artist_slug>/concerts/<str:concert_slug>/edit", edit_concert, name="concert_edit"),

    # auth
    path("auth/signup", signup_page, name="signup"),
    path("auth/login", login_page, name="login"),
    path("auth/logout", logout, name="logout"),

    # API
    path("api/artists", api_artist_list, name="api_artist_list"),
    path("api/artist/link", api_artist_link, name="api_artist_link"),
    path("api/concerts/attend", api_concert_attend, name="api_concert_attend"),
    path("api/concerts/rate", api_concert_rate, name="api_concert_rate"),
    path("api/concerts/update", api_concert_update, name="api_concert_update"),
    path("api/concerts/delete", api_concert_delete, name="api_concert_delete"),
    path("api/concerts/comment", api_comment, name="api_comment"),

    # other apps
    path('admin/', admin.site.urls),
    path("select2/", include("django_select2.urls"))
]
