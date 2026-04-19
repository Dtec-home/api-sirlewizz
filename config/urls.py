from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from strawberry.django.views import GraphQLView
from schema import schema
from payments.views import daraja_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(schema=schema))),
    path('api/mpesa/webhook/', daraja_callback),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
