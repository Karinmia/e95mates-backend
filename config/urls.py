from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import ListSavedLocations, SavedLocationView


def health_check(request):
    return HttpResponse(status=200)


urlpatterns = [
    path('', health_check),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),

    path('locations/', ListSavedLocations.as_view(), name='ListSavedLocations'),
    path('locations/<int:pk>', SavedLocationView.as_view(), name='getUpdateDeleteLocation'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG is True:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
