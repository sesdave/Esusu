from django.conf.urls import include, url
from rest_framework import routers

from group_invitation.api import views

router = routers.SimpleRouter()

urlpatterns = router.urls + [
    url('allmembers', views.ListGroupMembersAPIView.as_view(), name='list_member'),
    url('contribute', views.ContributeMemberAPIView.as_view(), name='member_contribution'),
    url('create_group', views.CreateGroupAPIView.as_view(), name='create_group'),
    url('search_groups', views.SearchListAPIView.as_view(), name='list_groups'),
    url('member', views.AddGroupMemberAPIView.as_view(), name='add_member'),
    url('accept_invitation/(?P<pk>\w+)', views.AcceptInvitationAPIView.as_view(), name='accept_invitation'),
    url('(?P<pk>[0-9]+)/invite/', views.InviteToTeamAPIView.as_view(), name='invite_to_team'),

]
