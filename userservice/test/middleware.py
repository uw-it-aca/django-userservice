from django.test import TestCase
from django.conf import settings
from django.test.client import RequestFactory
from userservice.user import UserServiceMiddleware, UserService

class TestMiddleware(TestCase):
    def test_basic(self):
        """
        Test that we do the right thing with no user in session
        """
        middleware = UserServiceMiddleware()
        request = RequestFactory().get("/")
        request.session = {}

        with self.settings(DEBUG=True):
            middleware.process_request(request)
            self.assertEquals(UserService().get_user(), None)
            middleware.process_response(request, None)

        with self.settings(DEBUG=False):
            middleware.process_request(request)
            self.assertEquals(UserService().get_user(), None)
            middleware.process_response(request, None)
