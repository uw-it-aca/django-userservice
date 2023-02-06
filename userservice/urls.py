# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.urls import re_path
from userservice.views import support


urlpatterns = [
    re_path(r'^$', support, name='userservice_override'),
]
