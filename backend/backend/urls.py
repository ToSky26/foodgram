from django.contrib import admin
from django.urls import path, include

from recipes.views import short_link_redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
    path('s/<str:short_link>/', short_link_redirect),
]
