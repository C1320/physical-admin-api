"""Applets URL Configuration

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
from django.urls import path, include
from django.conf.urls import url
from pc_api import views

urlpatterns = [
    url(r'^userDetails', views.userDetailsView.as_view()),  # 用户详情
    url(r'^userTotal', views.userTotalView.as_view()),  # 当前机构的用户数
    url(r'^userList', views.getUserListView.as_view()),  # 登录
    url(r'^login', views.loginView.as_view()),  # 登录
    url(r'^test', views.test.as_view()),
]