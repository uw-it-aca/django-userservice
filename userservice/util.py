import re
from django.conf import settings


def get_username():
    return getattr(settings, "REMOTE_USER_FORMAT", "eppn")


def expect_uwnetid():
    username_format = get_username()
    return username_format is not None and username_format.lower() == "uwnetid"


EPPN_PATTERN =\
    re.compile(r'^([a-z][_a-z0-9]{0,32})@[a-z0-9_-]+\.[a-z]+$', re.I)


def get_uid(username):
    if username is not None and len(username) and expect_uwnetid():
        found = re.match(EPPN_PATTERN, username)
        if found and found.group(1) and len(found.group(1)):
            return found.group(1)
    return username
