import logging
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.decorators import login_required
from importlib import import_module
from userservice.user import (get_original_user, set_override_user,
                              get_override_user, clear_override)


@login_required
def support(request):
    # timer = Timer()
    logger = logging.getLogger(__name__)

    override_error_username = None
    override_error_msg = None
    # Do the group auth here.

    actual_user = get_original_user(request)
    if not actual_user:
        raise Exception("No user in session")

    can_override = _get_override_auth_module()
    if not can_override():
        return render(request, 'no_access.html', {})

    if "override_as" in request.POST:
        transformation_module = _get_username_transform_module()
        new_user = transformation_module(request.POST["override_as"])
        validation_module = _get_validation_module()
        validation_error = validation_module(new_user)
        if validation_error is None:
            logger.info("%s is impersonating %s",
                        actual_user,
                        new_user)
            set_override_user(request, new_user)
        else:
            override_error_username = new_user
            override_error_msg = validation_error

    if "clear_override" in request.POST:
        logger.info("%s is ending impersonation of %s",
                    actual_user,
                    get_override_user(request))
        clear_override(request)

    context = {
        'original_user': actual_user,
        'override_user': get_override_user(request),
        'override_error_username': override_error_username,
        'override_error_msg': override_error_msg,
    }

    try:
        template_name = "userservice/user_override_extra_info.html"
        template.loader.get_template(template_name)
        context['has_extra_template'] = True
        context['extra_template'] = template_name
    except template.TemplateDoesNotExist:
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    try:
        template.loader.get_template("userservice/user_override_wrapper.html")
        context['wrapper_template'] = 'userservice/user_override_wrapper.html'
    except template.TemplateDoesNotExist:
        context['wrapper_template'] = 'support_wrapper.html'
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    return render(request,
                  'support.html',
                  context)


def _get_username_transform_module():
    if hasattr(settings, "USERSERVICE_TRANSFORMATION_MODULE"):
        return _get_module(settings.USERSERVICE_TRANSFORMATION_MODULE)
    else:
        return transform


def _get_validation_module():
    if hasattr(settings, "USERSERVICE_VALIDATION_MODULE"):
        return _get_module(settings.USERSERVICE_VALIDATION_MODULE)
    else:
        return validate


def _get_override_auth_module():
    if hasattr(settings, "USERSERVICE_OVERRIDE_AUTH_MODULE"):
        return _get_module(settings.USERSERVICE_OVERRIDE_AUTH_MODULE)
    else:
        return can_override


def _get_module(base):
    module, attr = base.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))
    try:
        validation_module = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a '
                                   '"%s" class' % (module, attr))
    return validation_module


def can_override():
    """
    The up stream app needs to defined can_override function and set
    USERSERVICE_OVERRIDE_AUTH_MODULE = app...can_override in your settings.py"
    """
    print("%s %s" % ("Your app needs to defined the can_override() function",
                     "to check if the original user has the permission."))
    print("Set USERSERVICE_OVERRIDE_AUTH_MODULE to that in the settings.py")
    return False


def validate(username):
    error_msg = "No override user supplied"
    if (len(username) > 0):
        error_msg = None
    return error_msg


def transform(username):
    return username.strip()
