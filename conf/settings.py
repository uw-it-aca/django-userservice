import sys

INSTALLED_APPS += [
    'userservice',
]

MIDDLEWARE += [
    'userservice.user.UserServiceMiddleware',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'add_user': {
            '()': 'userservice.logging.UserFilter'
        }
    },
    'formatters': {
        'include_user': {
            'format': '%(levelname)-4s %(asctime)s %(user)s %(actas)s %(message)s [%(name)s]',
            'datefmt': '[%Y-%m-%d %H:%M:%S]',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'filters': ['add_user'],
            'formatter': 'include_user',
        }
    },
    'loggers': {
        'userservice': {
            'handlers': ['stdout'],
        }
    }
}
