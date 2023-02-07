# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django import template
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.generic import TemplateView
from userservice.decorators import override_admin_required
from userservice.user import (
    get_original_user, set_override_user, get_override_user, clear_override)
from logging import getLogger
import json

logger = getLogger(__name__)


@method_decorator(override_admin_required, name='dispatch')
def SupportView(TemplateView):
    http_method_names = ['get', 'post']
    template_name = 'support.html'
    override_error_username = None
    override_error_msg = None

    def get_context_data(self, **kwargs):
        context = {
            'original_user': get_original_user(self.request),
            'override_user': get_override_user(self.request),
            'override_error_username': self.override_error_username,
            'override_error_msg': self.override_error_msg,
            'has_extra_template': False,
            'extra_template': None,
            'wrapper_template': 'support_wrapper.html',
        }

        try:
            extra_name = 'userservice/user_override_extra_info.html'
            template.loader.get_template(extra_name)
            context['has_extra_template'] = True
            context['extra_template'] = extra_name
        except template.TemplateDoesNotExist:
            pass

        try:
            wrapper_name = 'userservice/user_override_wrapper.html'
            template.loader.get_template(wrapper_name)
            context['wrapper_template'] = wrapper_name
        except template.TemplateDoesNotExist:
            pass

        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            content = json.loads(request.body)
        else:
            content = request.POST

        if 'override_as' in content:
            self.begin_override(content['override_as'])
        elif 'clear_override' in content:
            self.clear_override()

    def begin_override(self, override_as):
        transformation_module = self.get_username_transform_module()
        validation_module = self.get_validation_module()

        new_user = transformation_module(override_as)
        validation_error = validation_module(new_user)

        if validation_error is None:
            logger.info('{} is impersonating {}'.format(
                get_original_user(self.request), new_user))
            set_override_user(self.request, new_user)
        else:
            self.override_error_username = new_user
            self.override_error_msg = validation_error

    def clear_override(self):
        logger.info('{} is ending impersonation of {}'.format(
            get_original_user(self.request), get_override_user(self.request)))
        clear_override(self.request)

    @staticmethod
    def get_username_transform_module():
        if hasattr(settings, 'USERSERVICE_TRANSFORMATION_MODULE'):
            return import_string(settings.USERSERVICE_TRANSFORMATION_MODULE)
        else:
            return transform

    @staticmethod
    def get_validation_module():
        if hasattr(settings, 'USERSERVICE_VALIDATION_MODULE'):
            return import_string(settings.USERSERVICE_VALIDATION_MODULE)
        else:
            return validate


def validate(username):
    if not len(username):
        return 'No override user supplied'


def transform(username):
    return username.strip()
