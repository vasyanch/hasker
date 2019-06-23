from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


from qa import views as qa_views
from utils import common_views


urlpatterns = [
    path('', qa_views.IndexView.as_view(), name='index'),
    path('qa/', include('qa.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api_hasker.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = common_views.NotFoundView.as_view()
handler500 = common_views.ServerErrorView.as_view()
