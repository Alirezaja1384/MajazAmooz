import debug_toolbar

from django.contrib import admin
from django.urls import (path, include)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('learning.urls')),
    path('admin/', admin.site.urls),
    path('ajax/', include('ajax.urls')),

    # debug-toolbar
    path('__debug__/', include(debug_toolbar.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
