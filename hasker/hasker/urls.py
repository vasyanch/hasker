from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from qa import views as qa_views


urlpatterns = [
    path('', qa_views.IndexView.as_view(), name='index'),
    path('qa/', include('qa.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'qa.views.not_found'
handler500 = 'qa.views.server_error'
