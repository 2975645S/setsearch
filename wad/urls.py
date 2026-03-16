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
from setsearch.views.api import *
from setsearch.views.auth import *

urlpatterns = [
    path('admin/', admin.site.urls),

    # SetSearch
    path("", home_page, name="home"),
    path("artist/<str:artist_slug>", view_artist, name="artist"),
    path("create", create_concert, name = "create_concert"),
    path("artist/<str:artist_slug>/<str:concert_slug>", view_concert, name="concert"),


    # Auth
    path("signup", signup_page, name="signup"),
    path("login", login_page, name="login"),
    path("logout", logout, name="logout"),

    # API
    path("api/artists/list", list_artists),
    # path("api/comments/<int:comment_id>/delete", delete_comment, name="delete_comment"),
    # path("api/comments/create/<str:concert_id>", create_comment, name="create_comment"),

    # Other
    path("select2/", include("django_select2.urls"))
]
