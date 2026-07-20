from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from gestor.views import admin_password_change_guard,LandingPageView
urlpatterns = [

    path(
        'password_change/',
        admin_password_change_guard,
        name='password_change_guard' # Le damos un nombre único
    ),
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing'),

] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
