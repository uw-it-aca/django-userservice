from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'userservice.views',
    url(r'', 'support', name="override"),
)
