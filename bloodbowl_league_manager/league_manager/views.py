from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Team, Player, PlayerType, League, Match, Touchdown, PassCompletion, Casualty, Interception, MostValuablePlayer, InjuryType, Injury
from .forms import TeamForm, ModifyPlayerForm, AddPlayerForm, ModifyTeamForm
from django.db.models import Count, Q, F

def get_lowest_available_number(team):
    """
    Finds the lowest available positive integer for the player number on the given team.
    """
    used_numbers = set(Player.objects.filter(team=team).values_list('number', flat=True))
    number = 1
    while number in used_numbers:
        number += 1
    return number


def index(request):
    return render(request, 'league_manager/index.html')

def teams(request):
    teams = Team.objects.all()
    return render(request, 'league_manager/teams.html', {'teams': teams})

def create_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to index page after successful form submission
    else:
        form = TeamForm()
    
    return render(request, 'league_manager/create_team.html', {'form': form})

def team_details(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    players = team.players.all().order_by('number')  # Get all players for the team
    context = {
        "team": team,
        "players": players,
    }
    return render(request, "league_manager/team_details.html", context)


def modify_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # If the request is a POST, that means the form is being submitted
    if request.method == 'POST':
        form = ModifyPlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()  # Save the updated player
            return redirect('team_details', team_id=player.team.id)  # Redirect back to the team details page
    else:
        form = ModifyPlayerForm(instance=player)

    return render(request, 'league_manager/modify_player.html', {'form': form, 'player': player})


def add_player(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == "POST":
        form = AddPlayerForm(request.POST, team=team)
        if form.is_valid():
            player_name = form.cleaned_data['name']
            player_type = form.cleaned_data['player_type']

            # Create the new Player
            player = Player.objects.create(
                name=player_name,
                number = get_lowest_available_number(team),
                player_type=player_type,
                team=team
            )

            # Initialize stats from PlayerType
            player.position = player_type.position
            player.value = player_type.price
            player.strength = player_type.strength
            player.agility = player_type.agility
            player.movement = player_type.movement
            player.armour = player_type.armour
            player.skills = player_type.starting_skills
            player.normal_skill_access = player_type.normal_skill_access
            player.double_skill_access = player_type.double_skill_access
            player.save()

            return redirect('team_details', team_id=team.id)
    else:
        form = AddPlayerForm(team=team)

    return render(request, 'league_manager/add_player.html', {'form': form, 'team': team})


def remove_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST":
        status = request.POST.get("status")
        if status in ['Retired', 'Dead']:
            team = player.team
            player.status = status
            player.team = None  # Set team to null
            player.save()
            return redirect('team_details', team_id=team.id)

    return render(request, 'league_manager/remove_player.html', {'player': player})

def modify_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST':
        form = ModifyTeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return redirect('team_details', team_id=team.id)  # Redirect to the team details page after saving
    else:
        form = ModifyTeamForm(instance=team)

    return render(request, 'league_manager/modify_team.html', {'form': form, 'team': team})

def league_list(request):
    leagues = League.objects.all()
    return render(request, 'league_manager/league_list.html', {'leagues': leagues})

def league_details(request, league_id):
    league = get_object_or_404(League, id=league_id)
    teams = Team.objects.filter(league=league)
    matches_completed = Match.objects.filter(league=league, status="completed").order_by('-id')
    matches_in_progress = Match.objects.filter(league=league, status="in_progress").order_by('-id')

    team_stats = []

    for team in teams:
        name = team.name
        team_id = team.id

        # Wins
        wins_as_team1 = [m for m in team.matches_as_team1.all() if m.status == "completed" and (score := m.get_score())[0] > score[1]]
        wins_as_team2 = [m for m in team.matches_as_team2.all() if m.status == "completed" and (score := m.get_score())[0] < score[1]]
        wins = wins_as_team1 + wins_as_team2
        n_wins = len(wins)

        # Losses
        losses_as_team1 = [m for m in team.matches_as_team1.all() if m.status == "completed" and (score := m.get_score())[0] < score[1]]
        losses_as_team2 = [m for m in team.matches_as_team2.all() if m.status == "completed" and (score := m.get_score())[0] > score[1]]
        losses = losses_as_team1 + losses_as_team2
        n_losses = len(losses)

        # draws
        draws_as_team1 = [m for m in team.matches_as_team1.all() if m.status == "completed" and (score := m.get_score())[0] == score[1]]
        draws_as_team2 = [m for m in team.matches_as_team2.all() if m.status == "completed" and (score := m.get_score())[0] == score[1]]
        draws = draws_as_team1 + draws_as_team2
        n_draws = len(draws)

        # Points
        points = 3 * n_wins + n_draws

        # TDs
        tds_scored = team.team_touchdowns.filter(match__league=league, match__status="completed").count()

        tds_against = Touchdown.objects.filter(match__league=league,
                                               match__status="completed"
                                               ).exclude(
                                                   team=team
                                                   ).filter(
                                                       Q(match__team1=team) | Q(match__team2=team)
                                                       ).count()



        team_stats.append({
            'name':name,
            'team_id':team_id,
            'n_wins':n_wins,
            'n_lost':n_losses,
            'n_draws':n_draws,
            'points':points,
            'tds_scored':tds_scored,
            'tds_against':tds_against,
        })

        team_stats = sorted(team_stats, key=lambda x: (x['points'], x['tds_scored']), reverse=True)



    context = {
        'league': league,
        'teams': teams,
        'team_stats':team_stats,
        'matches_completed': matches_completed,
        'matches_in_progress': matches_in_progress,
    }
    return render(request, 'league_manager/league_details.html', context)

def add_match(request, league_id):
    
    league = get_object_or_404(League, id=league_id)
    league_name = league.name
    teams = Team.objects.filter(league=league)

    print(teams)
    
    context = {
        'league_id':league_id,
        'league_name':league_name,
        'teams':teams
        }
    
    return render(request, 'league_manager/add_match.html', context)
"""
def start_match(request, league_id, team1_id, team2_id):

    match = Match.objects.create(league_id, team1_id, team2_id)

    return redirect('match_page', match_id=match.id)
"""

def get_team_value(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    return JsonResponse({'team_value': team.get_total_team_value()})

def start_match(request, league_id, team1_id, team2_id):
    
    match = Match.objects.create(league_id=league_id, team1_id=team1_id, team2_id=team2_id)
    return redirect('match_page', match_id=match.id)

def end_match(request, match_id):
    
    match = get_object_or_404(Match, id=match_id)
    match.status = "completed"
    match.save()

    return redirect('league_details', league_id=match.league.id)

def cancel_match(request, match_id):
    
    match = get_object_or_404(Match, id=match_id)
    match.delete()

    return redirect('league_details', league_id=match.league.id)

def match_page(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    league = match.league
    team1 = match.team1
    team2 = match.team2
    team1_touchdowns, team2_touchdowns  = match.get_teams_tds()
    team1_completions, team2_completions  = match.get_teams_completions()
    team1_casualties, team2_casualties  = match.get_teams_casualties()
    team1_score, team2_score  = match.get_score()
    in_progress = match.status == "in_progress"

    context = {
        'match': match,
        'league': league,
        'team1': team1,
        'team2': team2,
        'team1_touchdowns':team1_touchdowns,
        'team2_touchdowns':team2_touchdowns,
        'team1_completions':team1_completions,
        'team2_completions':team2_completions,
        'team1_casualties':team1_casualties,
        'team2_casualties':team2_casualties,
        'team1_score': team1_score,
        'team2_score': team2_score,
        'in_progress': in_progress,
    }

    return render(request, 'league_manager/match_page.html', context)

def add_completion(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)

    players = team.players.all()

    if request.method == 'POST':
        thrower_id = request.POST.get('thrower_id')
        thrower = get_object_or_404(Player, id=thrower_id)
        receiver_id = request.POST.get('receiver_id')
        receiver = get_object_or_404(Player, id=receiver_id)

        PassCompletion.objects.create(match=match, thrower=thrower, receiver=receiver, team=team)

        return redirect('match_page', match_id=match_id)
    
    context = {
        'team':team,
        'match':match,
        'players':players,
    }

    return render(request, 'league_manager/add_completion.html', context)

def add_casualty(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)
    injury_types = InjuryType.objects.all()

    players = team.players.all()
    opposing_team = match.team1 if match.team2 == team else match.team2
    opposing_players = opposing_team.players.all()

    if request.method == 'POST':
        causing_player_id = request.POST.get('causing_player_id')
        causing_player = get_object_or_404(Player, id=causing_player_id)
        victim_player_id = request.POST.get('victim_player_id')
        victim_player = get_object_or_404(Player, id=victim_player_id)
        injury_type_id = request.POST.get('injury_type_id')
        injury_type = get_object_or_404(InjuryType, id=injury_type_id)

        Casualty.objects.create(match=match, causing_player=causing_player, victim_player=victim_player, causing_team=team, victim_team=opposing_team)
        Injury.objects.create(match=match, player=victim_player, injury_type=injury_type)

        return redirect('match_page', match_id=match_id)
    
    context = {
        'team':team,
        'match':match,
        'players':players,
        'opposing_players':opposing_players,
        'injury_types': injury_types
    }
    
    return render(request, 'league_manager/add_casualty.html', context)

def add_interception(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)

    players = team.players.all()
    opposing_team = match.team1 if match.team2 == team else match.team2
    opposing_players = opposing_team.players.all()

    if request.method == 'POST':
        intercepting_player_id = request.POST.get('intercepting_player_id')
        intercepting_player = get_object_or_404(Player, id=intercepting_player_id)
        throwing_player_id = request.POST.get('throwing_player_id')
        throwing_player = get_object_or_404(Player, id=throwing_player_id)

        Interception.objects.create(match=match, intercepting_player=intercepting_player, throwing_player=throwing_player, intercepting_team=team, throwing_team=opposing_team)

        return redirect('match_page', match_id=match_id)
    
    context = {
        'team':team,
        'match':match,
        'players':players,
        'opposing_players':opposing_players,
    }
    
    return render(request, 'league_manager/add_interception.html', context)

def add_touchdown(request, match_id, team_id):
    # Get the match and team objects
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)
    
    # Get the players associated with this team
    players = team.players.all()  # Assuming Team has a reverse relationship to Player
    
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        player = get_object_or_404(Player, id=player_id)

        # Create the Touchdown record
        Touchdown.objects.create(match=match, player=player, team=team)

        # Redirect to match page or another page
        return redirect('match_page', match_id=match.id)
    
    context = {
        'match': match,
        'team': team,
        'players': players
    }

    return render(request, 'league_manager/add_touchdown.html', context)

