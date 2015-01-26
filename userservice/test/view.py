from django.test import TestCase
from django.conf import settings
from django.test import Client
from django.test.client import RequestFactory
from django.test.utils import override_settings
from unittest2 import skipIf
from django.core.urlresolvers import reverse
from userservice.test import get_user
from userservice.user import UserServiceMiddleware, UserService

def missing_url(name):
    try:
        url = reverse(name)
    except Exception as ex:
        print(ex)
        return True
    return False


@override_settings(MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
    AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',),
    USERSERVICE_ADMIN_GROUP = "x",
)
class TestView(TestCase):
    @skipIf(missing_url("override"), "URLs not configured")

    @override_settings(AUTHZ_GROUP_BACKEND = 'authz_group.authz_implementation.all_ok.AllOK')
    def test_override(self):
        c = Client()

        get_user('javerage')
        c.login(username='javerage', password='pass')

        response = c.post(reverse("override"), { "override_as": "testover" })

        request = RequestFactory().get("/")
        request.session = c.session
        request.user = get_user('javerage')

        UserServiceMiddleware().process_request(request)

        self.assertEquals(UserService().get_user(), 'testover')
        self.assertEquals(UserService().get_acting_user(), 'javerage')
        self.assertEquals(UserService().get_original_user(), 'javerage')
        self.assertEquals(UserService().get_override_user(), 'testover')

        UserServiceMiddleware().process_response(request, response)

        response = c.post(reverse("override"), { "clear_override": 1})

        request = RequestFactory().get("/")
        request.session = c.session
        request.user = get_user('javerage')

        UserServiceMiddleware().process_request(request)

        self.assertEquals(UserService().get_user(), 'javerage')
        self.assertEquals(UserService().get_acting_user(), 'javerage')
        self.assertEquals(UserService().get_original_user(), 'javerage')
        self.assertEquals(UserService().get_override_user(), None)

        UserServiceMiddleware().process_response(request, response)

