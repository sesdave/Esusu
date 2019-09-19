from django.contrib import admin
from group_invitation.models import Group, GroupInvitation, GroupMember, Member, TeamInvitation

admin.site.register(Group)
admin.site.register(GroupInvitation)
admin.site.register(GroupMember)
admin.site.register(Member)
admin.site.register(TeamInvitation)


# Register your models here.
