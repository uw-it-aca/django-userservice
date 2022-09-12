# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf.urls import url
from userservice.views import support


urlpatterns = [
    url(r'', support, name="userservice_override"),
]
