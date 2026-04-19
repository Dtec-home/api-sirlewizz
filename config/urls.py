from django.contrib import admin
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from strawberry.django.views import GraphQLView
from schema import schema
from payments.views import daraja_callback
from django.http import FileResponse, Http404
from django.core.files.storage import default_storage

def serve_media_file(request, file_path):
    """Serve media files from storage (local or Backblaze)"""
    try:
        storage_path = f'products/{file_path}'
        if not default_storage.exists(storage_path):
            raise Http404("File not found")
        file_obj = default_storage.open(storage_path, 'rb')
        return FileResponse(file_obj)
    except Http404:
        raise
    except Exception as exc:
        raise Http404("File not found") from exc

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(schema=schema))),
    path('api/mpesa/webhook/', daraja_callback),
    re_path(r'^media/products/(?P<file_path>.*)$', serve_media_file),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
