# util.team

from flask import flash

from app.models import Account, Team
from app.util.password import make_password


def create_team(account, name):
    """
    ATTENTION:
    The following code is a workaround for a bug in MongoEngine.
    When removing the last element from a ListField and saving
    the document, it removes the field from the document.
    Therefore, we first look for teams without the field before
    finding ones with it missing.
    """

    # Let's assign them a team
    team = Team.objects.filter(members__exists=False).first()

    if team is None:
        team = Team.objects.filter(members__size=0).first()

    # More workaround code
    if team.members is None:
        team.members = [account]
    else:
        team.members.append(account)
    account.team = team

    # Set the team name
    rename_team(team, (name or team.teamID))
    team.save()
    account.save()

    return team


def set_division(team, division):
    team.division = division
    team.save()
    # TODO make this more...robust


def join_team(account, teamID=None, teamPass=None, team=None):

    # Look up the team if we didn't bring one
    if team is None:
        team = Team.objects(teamID=teamID, teamPass=teamPass).first()

    # We didn't bring a team nor did we find one
    if team is None:
        error = "Team with those credentials not found."

    # We have our team, let's try joining
    if team:
        # Max 3 members
        if not team.members:
            team.members = [account]  # See workaround notice above
            team.save()
            account.team = team
            account.save()
            return True
        elif len(team.members) < 3:
            team.members.append(account)
            account.team = team
            team.save()
            account.save()
            return True
        else:
            message = "Team %s already has 3 members".format(
                team.team_name or team.teamID)
            flash(message, 'error')
            return False

    flash("Error finding team", 'error')
    return False


def leave_team(account, team):
    account.team = None
    account.save()

    team.members.remove(account)

    # Clear name if last member, change teampass
    if len(team.members) is 0:
        team.members = []
        team.team_name = None
        team.division = None
        team.teamPass = make_password()
    team.save()

    success = "You have left the team."

    return success


def rename_team(team, name):
    team.team_name = name
    team.team_name = team.team_name[:Team.MAX_NAME_LENGTH]
    team.save()

    success = "Team name updated."

    return success
