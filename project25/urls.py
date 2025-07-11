
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views 

# ######
from app1.views import login_auth0, callback, logout_auth0

urlpatterns = [
    path('admin/', admin.site.urls,name="admin"),
    path('',include('app0.urls')), #this line includes the URLs from app0
    path('marketplace/',include('app1.urls')), # marketplace app URLs(app1)

    
    # path('accounts/',include('allauth.urls')), # allauth
    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/auth0/', login_auth0, name='login'),
    path('callback/', callback, name='callback'),
    path('logout/auth0/', logout_auth0, name='logout'),

]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


