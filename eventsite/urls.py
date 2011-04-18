# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$','eventsite.views.front_page', name="front-page"),
    url(r'^jumpto/$','eventsite.views.jumpto', name="jumpto"),
    url(r'^ical/$','eventsite.views.ical', name="ical"),
    url(r'^week-of/(?P<datestring>[\x20-\x7E]+)/(?P<format>[\x20-\x7E]+)$','eventsite.views.week_of_index', name="week-of-with-format"),
    url(r'^week-of/(?P<datestring>[\x20-\x7E]+)$','eventsite.views.week_of_index', name="week-of"),
)

