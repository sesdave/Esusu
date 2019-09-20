from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from invitations.adapters import get_invitations_adapter
from invitations.exceptions import (AlreadyAccepted, AlreadyInvited,
                                    UserRegisteredEmail)
from rest_framework import serializers

from group_invitation.models import GroupInvitation,Group, Member, TeamInvitation

User = get_user_model()

errors = {
    "already_invited": _("This e-mail address has already been"
                         " invited."),
    "already_accepted": _("This e-mail address has already"
                          " accepted an invite."),
    "email_in_use": _("An active user is using this e-mail address"),
}

class GroupCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['name', 'description', 'capacity', 'searchable']

    def validate(self, data):
        name = data.get('name')
        user = self.context.get('user', None)
        qs = Group.objects.filter(name__iexact=name, creator=user)
        if qs.exists():
            raise serializers.ValidationError("You already have a similar group Name.Use another name to create Group")
        if not user:
            raise serializers.ValidationError("User not found.")

        return data


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name', 'description']


class AddGroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('groupId',)

    def validate(self, data):
        user = self.context.get('user', None)
        group =data.get('groupId')
        #grouper = get_object_or_404(Group, pk=group)
        try:
            grouper = Group.objects.get(pk=group)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist.")
        capacity=grouper.capacity
        if not group:
            raise serializers.ValidationError("Group id not found")
        if not user:
            raise serializers.ValidationError("User not found.")

        if not Group.objects.filter( pk__iexact=group):
            raise serializers.ValidationError("Group does not exist")

        if Member.objects.filter( group=grouper).count()>=capacity:
            raise serializers.ValidationError("Maximum Capacity of this Group has been Reached, You cannot be added")

        if Member.objects.filter( name=user, group=grouper ):
            raise serializers.ValidationError("You are already part of this Group.")

        return data

class ContributeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('groupId','saving',)

    def validate(self, data):
        user = self.context.get('user', None)
        group =data.get('groupId')
        saving = data.get('saving')

        try:
            grouper = Group.objects.get(pk=group)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist.")
        if not saving:
            raise serializers.ValidationError("Put in a valid number")
        if not group:
            raise serializers.ValidationError("Group id not found")
        if not user:
            raise serializers.ValidationError("User not found.")

        if not Group.objects.filter( pk__iexact=group):
            raise serializers.ValidationError("Group does not exist")

        if not Member.objects.filter(name=user, group=grouper):
            raise serializers.ValidationError("Sorry, You do not belong to the group and hence cannot contribute.")
        return data



class ListGroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('member_name','groupId','saving',)
        read_only_fields=('name',)

    def validate(self, data):
        user = self.context.get('user', None)
        group =data.get('groupId')

        try:
            Group.objects.get(pk=group)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist.")
        if not group:
            raise serializers.ValidationError("Group id not found")
        if not user:
            raise serializers.ValidationError("User not found.")

        if not Group.objects.filter( pk__iexact=group):
            raise serializers.ValidationError("Group does not exist")

        if not Group.objects.filter(pk=group, creator=user):
            raise serializers.ValidationError("Sorry, you are not admin and cant view members")

        return data



class EmailListField(serializers.ListField):
    child = serializers.EmailField()


class InvitationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupInvitation
        fields = ('email',)

    def _validate_invitation(self, email):
        if GroupInvitation.objects.all_valid().filter(
                email__iexact=email, accepted=False):
            raise AlreadyInvited
        elif GroupInvitation.objects.filter(
                email__iexact=email, accepted=True):
            raise AlreadyAccepted
        elif get_user_model().objects.filter(email__iexact=email):
            raise UserRegisteredEmail
        else:
            return True

    def validate_email(self, email):
        email = get_invitations_adapter().clean_email(email)

        try:
            self._validate_invitation(email)
        except(AlreadyInvited):
            raise serializers.ValidationError(errors["already_invited"])
        except(AlreadyAccepted):
            raise serializers.ValidationError(errors["already_accepted"])
        except(UserRegisteredEmail):
            raise serializers.ValidationError(errors["email_in_use"])
        return email

    def create(self, validate_data):
        return GroupInvitation.create(**validate_data)


class InvitationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupInvitation
        fields = '__all__'


class InvitationBulkWriteSerializer(InvitationWriteSerializer):

    email = EmailListField()

    class Meta(InvitationWriteSerializer.Meta):
        model = GroupInvitation
        fields = InvitationWriteSerializer.Meta.fields

    def validate_email(self, email_list):
        if len(email_list) == 0:
            raise serializers.ValidationError(
                _('You must add one or more email addresses')
            )
        for email in email_list:
            email = get_invitations_adapter().clean_email(email)
            try:
                self._validate_invitation(email)
            except(AlreadyInvited):
                raise serializers.ValidationError(errors["already_invited"])
            except(AlreadyAccepted):
                raise serializers.ValidationError(errors["already_accepted"])
            except(UserRegisteredEmail):
                raise serializers.ValidationError(errors["email_in_use"])
            return email_list

class TeamInvitationCreateSerializer(serializers.Serializer):

    MAXIMUM_EMAILS_ALLOWED = 5

    emails = serializers.ListField(
        write_only=True
    )

    def validate(self, data):
        emails = data.get('emails')
        if len(emails) > self.MAXIMUM_EMAILS_ALLOWED:
            raise serializers.ValidationError("Not more than %s email ID's are allowed." % self.MAXIMUM_EMAILS_ALLOWED)

        team_pk = self.context.get('team_pk')
        user = self.context.get('user')
        data.success={"success":"Invite successfully to sent to mail"}
        if team_pk:
            data.id_group = team_pk
        try:
            team = Group.objects.get(pk=team_pk, creator=user)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Team does not exist.")

        if team.has_invite_permissions(user):
            email_ids_existing = User.objects.filter(email__in=emails).values_list('email', flat=True)
            if not email_ids_existing:
                raise serializers.ValidationError(
                    "This is not a registered user on this platform. (%s)"
                    % ",".join(email_ids_existing))
            return data

        raise serializers.ValidationError("Operation not allowed.")

class AcceptMemberInvitationSerializer(serializers.Serializer):

    def validate(self, data):
        code = self.context.get('code', None)

        invitation = TeamInvitation.objects.validate_code(code)
        if not invitation:
            raise serializers.ValidationError("Invite code is not valid / expired.")
        email=invitation.email
        user=User.objects.get(email__iexact=email)
        group=invitation.group
        data.user=user
        data.group = group

        if not group:
            raise serializers.ValidationError("Group not found")
        capacity=group.capacity

        if not user:
            raise serializers.ValidationError("User not found.")

        if Member.objects.filter( group=group).count()>=capacity:
            raise serializers.ValidationError("Maximum Capacity of this Group has been Reached, You cannot be added")

        if Member.objects.filter( name=user, group=group ):
            raise serializers.ValidationError("You are already part of this Group.")
        return data

