from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('data_parsin_link/', views.fetch_data_by_brand_or_part_group),
    path('', include('core_app.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
