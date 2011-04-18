from django.conf.urls.defaults import *
from tasks import migrate_events, migrate_profiles, migrate_sources

urlpatterns = patterns('eventsite.admin.views',
      url(r'^$','index', name="admin-home"),
      url(r'^create/$','create_site', name="create-site"),
      url(r'^logo/$','logo', name="logo-upload"),
      url(r'^edit/$','edit_site', name="edit-site"),
      url(r'^users/$','manage_users', name="manage-users"),
      url(r'^configure-mailchimp', 'configure_mailchimp', name="configure-mailchimp"),
      url(r'^migrate/$','migrate',),
      url(r'^migrate-events/$',migrate_events,),
      url(r'^migrate-profiles/$',migrate_profiles,),
      url(r'^migrate-sources/$',migrate_sources,),
      

)

