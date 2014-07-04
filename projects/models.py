from django.db import models
from django.conf import settings

from .manager import ProjectManager
from .base import STATUS


class Project(models.Model):
    """
    Stores a single project.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    isprivate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    everyone_contributes = models.BooleanField(default=True)
    all_contrib_isprivate = models.BooleanField(default=True)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='admins')

    objects = ProjectManager()

    def __str__(self):
        return self.name + ' status: ' + self.status + ' private: ' + str(self.isprivate)

    @classmethod
    def create(cls, name, description, isprivate, creator):
        """
        Creates a new project. Creates two usergroups and adds the creator to
        the administrators user group.
        """
        project = cls(
            name=name,
            description=description,
            isprivate=isprivate,
            creator=creator
        )

        project.save()
        project.admins.add(creator)

        return project

    def delete(self):
        """
        Removes the project from the listing of all projects by setting its
        status to `DELETED`.
        """
        self.status = STATUS.deleted
        self.save()

    def is_admin(self, user):
        """
        Returns True if the user is member of the administrators group, False
        if not.
        """
        return user in self.admins.all()

    def can_access(self, user):
        """
        Returns True if:
        - the user is member of the administrators group
        - the user is member of one of the usergroups
        - the project is public and has at least one public view
        """
        return self.status == STATUS.active and (self.is_admin(user) or (
            ((not self.isprivate and not self.all_contrib_isprivate) or
                self.views.filter(isprivate=False).exists()) or (
                not user.is_anonymous() and (
                    self.usergroups.filter(
                        can_contribute=True, users=user).exists() or
                    self.usergroups.filter(
                        can_moderate=True, users=user).exists() or
                    self.usergroups.filter(
                        view_all_contrib=True, read_all_contrib=True,
                        users=user).exists() or
                    self.usergroups.filter(
                        users=user, viewgroups__isnull=False))
                )
            )
        )

    def can_access_all_contributions(self, user):
        return self.is_admin(user) or not self.all_contrib_isprivate or (
            not user.is_anonymous() and (
                self.usergroups.filter(
                    view_all_contrib=True,
                    read_all_contrib=True,
                    users=user).exists()))

    def can_contribute(self, user):
        """
        Returns True if:
        - the user is member of the administrators group
        - the user is member of one usergroup that has can_contribute granted
        - everyone_contributes is True
        """
        return self.status == STATUS.active and (
            self.everyone_contributes or self.is_admin(user) or (
                not user.is_anonymous() and (
                    self.usergroups.filter(
                        can_contribute=True, users=user).exists())))

    def can_moderate(self, user):
        return self.status == STATUS.active and (
            self.is_admin(user) or (
                not user.is_anonymous() and (
                    self.usergroups.filter(
                        can_moderate=True, users=user).exists())))

    def is_involved(self, user):
        """
        Returns True if:
        - the user is member of the administrators group
        - the user is member of at least usergroup assigned to the project
        """
        return self.is_admin(user) or (
            not user.is_anonymous() and (
                self.usergroups.filter(users=user).exists()))
