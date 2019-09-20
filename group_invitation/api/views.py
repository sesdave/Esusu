from django.contrib import messages
from django.db.models import Q
from invitations.adapters import get_invitations_adapter
from django.contrib.sites.shortcuts import get_current_site
from invitations.app_settings import app_settings as invitations_settings
from invitations.signals import invite_accepted
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import (api_view,
                                       permission_classes,action)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from group_invitation.models import Group, Member, TeamInvitation
from .serializers import GroupCreateSerializer,GroupSerializer, AddGroupMemberSerializer,ListGroupMemberSerializer, ContributeMemberSerializer, TeamInvitationCreateSerializer, AcceptMemberInvitationSerializer
from accounts.permissions import IsOwnerOrReadOnly

class CreateGroupAPIView(generics.CreateAPIView):
    """
    Endpoint to create a group.

    """

    permission_classes = (IsAuthenticated, )
    serializer_class = GroupCreateSerializer
    queryset = Group.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user}
                                           )
        if serializer.is_valid(raise_exception=True):
            group = serializer.save(creator=request.user)
            member = Member.objects.create(name=request.user,group=group, groupId=0)
            member.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddGroupMemberAPIView(generics.CreateAPIView):
    """
    Endpoint to create a group.

    """

    permission_classes = (IsAuthenticated, )
    serializer_class = AddGroupMemberSerializer
    queryset = Member.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user}
                                           )
        if serializer.is_valid(raise_exception=True):
            group = serializer.validated_data.get('groupId')
            #group = 9
            group_add=Group.objects.get( pk=group )
            serializer.save(name=request.user,group=group_add )
            success_data={'success':'You have successfully joined this group'}
            return Response(success_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContributeMemberAPIView(generics.CreateAPIView):
    """
    Endpoint to contribute.

    """

    permission_classes = (IsAuthenticated, )
    serializer_class = ContributeMemberSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user}
                                           )
        if serializer.is_valid(raise_exception=True):
            group = serializer.validated_data.get('groupId')
            saving=serializer.validated_data.get('saving')
            group_add=Group.objects.get( pk=group )
            member=Member.objects.get(name=request.user, group=group_add)
            member.saving+=saving
            member.save();
            ano_serializer = ContributeMemberSerializer(member, many=False)
            success_data={'success':'You have successfully joined this group'}
            return Response(ano_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SearchListAPIView(generics.ListAPIView):
    """
    Endpoint to search available groups.

    """
    permission_classes = (IsAuthenticated, )
    serializer_class = GroupSerializer

    def get_queryset(self):
        qs = Group.objects.all()
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(Q(name__icontains=query), Q(searchable=True)).distinct()
        return qs



class ListGroupMembersAPIView(generics.ListAPIView):
    """
    Endpoint to search available groups.

    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )
    serializer_class = ListGroupMemberSerializer


    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user}
                                           )
        if serializer.is_valid(raise_exception=True):
            group = serializer.validated_data.get('groupId')
            #group = 9
            group_add=Group.objects.get( pk=group )
            member=Member.objects.filter( group=group_add )
            ano_serializer=ListGroupMemberSerializer(member, many=True)
            return Response(ano_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InviteToTeamAPIView(generics.CreateAPIView):
    """
    Endpoint to invite people to a team.

    """

    permission_classes = (IsAuthenticated, )
    serializer_class = TeamInvitationCreateSerializer
    queryset = TeamInvitation.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={
                                               'user': request.user,
                                               'team_pk': kwargs['pk']
                                           })
        if serializer.is_valid(raise_exception=True):
            email_ids = serializer.validated_data.get('emails')
            groupId = serializer.validated_data.id_group
            group = Group.objects.get(pk=groupId)
            self.create_invitations(email_ids=email_ids, invited_by=request.user, group=group)
            return Response(serializer.validated_data.success, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_invitations(self, email_ids, invited_by, group):
        invitations = [TeamInvitation(email=email_id, invited_by=invited_by, group=group)
                       for email_id in email_ids]
        invitations = TeamInvitation.objects.bulk_create(invitations)
        self.send_email_invites(invitations)

    def send_email_invites(self, invitations):
        # Sending email expected to be done asynchronously in production environment.
        for invitation in invitations:
            invitation.send_email_invite(get_current_site(self.request))

class AcceptInvitationAPIView(generics.CreateAPIView):
    """
    Endpoint to accept people to a team.

    """

    permission_classes = (AllowAny, )
    serializer_class = AcceptMemberInvitationSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={
                                               'code': kwargs['pk']
                                           })


        if serializer.is_valid(raise_exception=True):
            group = serializer.validated_data.group
            user = serializer.validated_data.user

            serializer.save(name=user, group=group)
            success_data = {'success': 'You have successfully joined this group'}
            return Response(success_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


