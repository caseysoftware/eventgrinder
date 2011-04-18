from django.conf.urls.defaults import *


urlpatterns = patterns('account',
      url(r'^signout/$', 'views.signout', name="account-signout"),
      url(r'^profile-setup', 'views.profile_setup', name='profile-setup'),
      url(r'^$', 'views.edit_profile', name="account-edit"),
)
