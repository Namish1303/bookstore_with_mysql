"""bookstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path

from views.views import home_page, userSign,user_profile,search,results,book_page,add,show_cart,checkout,track,track_order
from views.views import signOwner,owner_auth,removeBook,expenditure,authorR, genreR
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home',home_page,name= 'home'),
    path('user_autherization',userSign,name='user_signin'),
    path('user',user_profile,name="user_profile"),
    path('search',search,name="search"),
    path('result',results,name="search_results"),
    path('book',book_page,name="bookPage"),
    path('addToCart',add,name="add_cart"),
    path('cart',show_cart,name="cart"),
    path('checkout',checkout,name="checkout"),
    path('track',track,name="track_order"),
    path('track_order',track_order,name="track"),
    path('owner',signOwner,name="signInOwner"),
    path('owner_autherization',owner_auth,name="owner_signin"),
    path('remove',removeBook,name="removeBook"),
    path('datereport',expenditure,name="dateExpenditure"),
    path('authorreport',authorR,name="authorReport"),
    path('genrereport',genreR,name="genreReport"),
]
