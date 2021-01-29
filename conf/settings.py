
INSTALLED_APPS += [
    'userservice',
]

MIDDLEWARE += [
    'userservice.user.UserServiceMiddleware',
]
