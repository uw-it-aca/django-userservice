import re
from django.conf import settings


def _get_format():
    return getattr(settings, "REMOTE_USER_FORMAT", "eppn")


def expect_uid():
    username_format = _get_format()
    return username_format is not None and\
        (username_format == "uid" or username_format == "uwnetid")


EPPN_PATTERN =\
    re.compile(r'^([^@]+)@[a-z0-9_-]+\.[a-z]+$', re.I)


def get_uid(username):
    if username is not None and len(username) and expect_uid():
        found = re.match(EPPN_PATTERN, username)
        if found and found.group(1) and len(found.group(1)):
            return found.group(1)
    return username
