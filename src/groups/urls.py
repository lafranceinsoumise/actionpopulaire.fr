from django.conf.urls import url
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from . import views

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
simple_id = r'[0-9]+'


urlpatterns = [
    # groups views
    url('^groupes/creer/$', views.CreateSupportGroupView.as_view(), name='create_group'),
    url('^groupes/creer/form/$', views.PerformCreateSupportGroupView.as_view(), name='perform_create_group'),
    url('^groupes/liste/$', views.SupportGroupListView.as_view(), name='list_all_groups'),
    url(f'^groupes/(?P<pk>{uuid})/$', views.SupportGroupDetailView.as_view(), name='view_group'),
    url(f'^groupes/(?P<pk>{uuid})/manage/$', views.SupportGroupManagementView.as_view(), name='manage_group'),
    url(f'^groupes/(?P<pk>{uuid})/modifier/$', views.ModifySupportGroupView.as_view(), name='edit_group'),
    url(f'^groupes/(?P<pk>{uuid})/quitter/$', views.QuitSupportGroupView.as_view(), name='quit_group'),
    url(f'^groupes/(?P<pk>{uuid})/localisation/$', views.ChangeGroupLocationView.as_view(),
        name='change_group_location'),
    url(f'^groupes/retirer_gestionnaire/(?P<pk>{simple_id})/$', views.RemoveManagerView.as_view(),
        name='remove_manager'),

    url('^livrets_thematiques/$', views.ThematicBookletViews.as_view(), name="thematic_groups_list"),
]
