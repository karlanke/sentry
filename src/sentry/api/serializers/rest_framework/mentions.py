from __future__ import absolute_import

from rest_framework import serializers

from sentry.api.fields.actor import Actor
from sentry.models import (
    Team,
    User,
)


def extract_user_ids_from_mentions(organization_id, mentions):
    """
    Extracts user ids from a set of mentions. Mentions should be a list of
    `Actor` instances. Returns a dictionary with 'users' and 'team_users' keys.
    'users' is the user ids for all explicitly mentioned users, and 'team_users'
    is all user ids from explicitly mentioned teams, excluding any already
    mentioned users.
    """
    actors = Actor.resolve_many(mentions)
    actor_mentions = seperate_resolved_actors(actors)

    mentioned_team_users = list(
        Team.objects.get_users_from_teams(
            organization_id,
            actor_mentions['teams'],
        ).exclude(id__in={u.id for u in actor_mentions['users']}).values_list(
            'id',
            flat=True,
        )
    )

    return {
        'users': set([user.id for user in actor_mentions['users']]),
        'team_users': set(mentioned_team_users),
    }


def seperate_actors(actors):
    users = [actor for actor in actors if actor.type is User]
    teams = [actor for actor in actors if actor.type is Team]

    return {'users': users, 'teams': teams}


def seperate_resolved_actors(actors):
    users = [actor for actor in actors if isinstance(actor, User)]
    teams = [actor for actor in actors if isinstance(actor, Team)]

    return {'users': users, 'teams': teams}


class MentionsMixin(object):
    def validate_mentions(self, attrs, source):
        if source in attrs and 'group' in self.context:

            mentions = attrs[source]
            seperated_actors = seperate_actors(mentions)
            # Validate that all mentioned users exist and are on the project.
            users = seperated_actors['users']

            mentioned_user_ids = {user.id for user in users}

            project = self.context['group'].project

            user_ids = set(
                project.member_set.filter(user_id__in=mentioned_user_ids)
                .values_list('user_id', flat=True)
            )

            if len(mentioned_user_ids) > len(user_ids):
                raise serializers.ValidationError('Cannot mention a non team member')

            # Validate that all mentioned teams exist and are on the project.
            teams = seperated_actors['teams']
            mentioned_team_ids = {team.id for team in teams}

            if len(mentioned_team_ids) > project.teams.filter(
                    id__in={t.id for t in teams}).count():
                raise serializers.ValidationError(
                    'Mentioned team not found or not associated with project')

        return attrs