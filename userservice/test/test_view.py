from django.test import TestCase
from django.conf import settings
from django.test import Client
from django.test.client import RequestFactory
from django.test.utils import override_settings
from unittest2 import skipIf
from django.core.urlresolvers import reverse
from userservice.test import get_user as get_django_user
from userservice.user import get_user, get_acting_user, get_override_user
from userservice.user import get_original_user, set_override_user

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
)
class TestView(TestCase):

    @skipIf(missing_url("userservice_override"), "URLs not configured")
    def test_cannot_override(self):
        c = Client()
        get_django_user('javerage')
        c.login(username='javerage', password='pass')
        request = RequestFactory().get("/")
        request.session = c.session
        request.user = get_django_user('javerage')
        response = c.post(reverse("userservice_override"),
                          { "override_as": "testover" })
        self.assertEquals(response.status_code, 401)

    @skipIf(missing_url("userservice_override"), "URLs not configured")
    @override_settings(USERSERVICE_OVERRIDE_AUTH_MODULE='userservice.test.can_override')
    def test_override(self):
        c = Client()

        get_django_user('javerage')
        c.login(username='javerage', password='pass')

        request = RequestFactory().get("/")
        request.session = c.session
        request.user = get_django_user('javerage')

        response = c.post(reverse("userservice_override"), { "override_as": "testover" })
        request.session = c.session

        self.assertEquals(get_user(request), 'testover')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_original_user(request), 'javerage')
        self.assertEquals(get_override_user(request), 'testover')

        response = c.post(reverse("userservice_override"), { "clear_override": 1})

        request = RequestFactory().get("/")
        request.session = c.session

        self.assertEquals(get_user(request), 'javerage')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_original_user(request), 'javerage')
        self.assertEquals(get_override_user(request), None)

    @override_settings(USERSERVICE_OVERRIDE_AUTH_MODULE='userservice.test.can_override',
                       USERSERVICE_VALIDATION_MODULE='userservice.test.under8')
    def test_validation(self):
        c = Client()

        get_django_user('javerage')
        c.login(username='javerage', password='pass')


        request = RequestFactory().get("/")
        request.session = c.session
        request.user = get_django_user('javerage')

        response = c.post(reverse("userservice_override"), { "override_as": "testover8" })

        self.assertEquals(get_user(request), 'javerage')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_original_user(request), 'javerage')
        self.assertEquals(get_override_user(request), None)

    @override_settings(USERSERVICE_OVERRIDE_AUTH_MODULE='userservice.test.can_override',
                       USERSERVICE_VALIDATION_MODULE='userservice.test.over8')
    def test_validation2(self):
        c = Client()

        get_django_user('javerage')
        c.login(username='javerage', password='pass')


        request = RequestFactory().get("/")
        request.session = c.session
        request.user = get_django_user('javerage')

        response = c.post(reverse("userservice_override"), { "override_as": "testover8" })

        self.assertEquals(get_user(request), 'testover8')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_original_user(request), 'javerage')
        self.assertEquals(get_override_user(request), 'testover8')


    @override_settings(USERSERVICE_OVERRIDE_AUTH_MODULE='userservice.test.can_override',
                       USERSERVICE_TRANSFORMATION_MODULE='userservice.test.add_washington')
    def test_transform(self):
        c = Client()

        get_django_user('javerage')
        c.login(username='javerage', password='pass')


        request = RequestFactory().get("/")
        request.session = c.session
        request.user = get_django_user('javerage')

        response = c.post(reverse("userservice_override"), { "override_as": "testover8" })

        self.assertEquals(get_user(request), 'testover8@uw.edu')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_original_user(request), 'javerage')
        self.assertEquals(get_override_user(request), 'testover8@uw.edu')
