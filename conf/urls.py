from django.conf.urls import include, url

urlpatterns = [
    url(r'^user/', include('userservice.urls')),
]

