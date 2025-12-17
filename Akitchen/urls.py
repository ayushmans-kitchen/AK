from django.contrib import admin
from django.urls import path, include

from Customers import urls as csurls
from Admin import urls as adurls

urlpatterns = [
    path('devspannel/', admin.site.urls),
    path('', include(csurls)),
    path('ayushman/admin/', include(adurls)),
]

