from django.contrib import admin
from django.urls import path, include
from .views import home
from Customers import urls as csurls
from Admin import urls as adurls

urlpatterns = [
    path('devspannel/', admin.site.urls),
    path('', include(csurls)),
    path('a/',home),
    path('ayushman/admin/', include(adurls)),
]

