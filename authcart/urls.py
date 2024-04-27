from django.urls import path
from authcart import views

urlpatterns=[
    path('signup/',views.handlesignup,name='signup'),
    path('login/',views.handlelogin,name='handlelogin'),
    path('logout/',views.handlelogout,name='handlelogout'),
    path('activate/<uidb64>/<token>',views.ActivateUserAccountView.as_view(),name='activate')
]