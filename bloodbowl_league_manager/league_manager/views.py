from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Team, Player, PlayerType, League, Match, Touchdown, PassCompletion, Casualty, Interception, MostValuablePlayer, InjuryType, Injury, LevelUpType, LevelUp
from .forms import TeamForm, ModifyPlayerForm, AddPlayerForm, ModifyTeamForm, LeagueForm
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

def factions(request):
    return render(request, 'league_manager/factions.html')

def create_league(request):
    if request.method == 'POST':
        form = LeagueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('leagues')
    else:
        form = LeagueForm()
    
    return render(request, 'league_manager/create_league.html', {'form':form})

def join_league(request, team_id):
    leagues = League.objects.all()
    team = get_object_or_404(Team, id=team_id)

    if team.league:
        team.league = None
        team.save()
        return redirect('team_details', team_id = team.id)
    
    if request.method == 'POST':
        league_id = request.POST.get('league_id')
        team.league = get_object_or_404(League, id = league_id)
        team.save()

        return redirect('team_details', team_id = team_id)
    
    content = {
        'team':team,
        'leagues':leagues
    }

    return render(request, 'league_manager/join_league.html', content)

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

    if request.method == 'POST':
        new_number = request.POST.get('player_number')
        new_name = request.POST.get('player_name')

        player.name = new_name
        player.number = new_number

        player.save()

        return redirect('team_details', player.team.id)

    return render(request, 'league_manager/modify_player.html', {'player': player})

def add_level_up(request, player_id):

    player = get_object_or_404(Player, id=player_id)

    allowed_categories = set(player.normal_skill_access) | set(player.double_skill_access)  # Combine both

    allowed_categories.add("stat_increase")
    print(allowed_categories)
    skills_by_group = {}

    if "G" in allowed_categories:
        skills_by_group["General"] = LevelUpType.objects.filter(category="G")
    if "A" in allowed_categories:
        skills_by_group["Agility"] = LevelUpType.objects.filter(category="A")
    if "S" in allowed_categories:
        skills_by_group["Strength"] = LevelUpType.objects.filter(category="S")
    if "P" in allowed_categories:
        skills_by_group["Passing"] = LevelUpType.objects.filter(category="P")
    if "M" in allowed_categories:
        skills_by_group["Mutation"] = LevelUpType.objects.filter(category="M")
    if "stat_increase" in allowed_categories:
        skills_by_group["Stat Increase"] = LevelUpType.objects.filter(category__in=["+MA", "+ST", "+AG", "+AV"])


    if request.method == "POST":
        level_up_id = request.POST.get('level_up')
        level_up = get_object_or_404(LevelUpType, id=level_up_id)

        LevelUp.objects.create(player=player, level_up_type=level_up)

        return redirect('team_details', team_id=player.team.id)
    
    context = {
        'player':player,
        'skills':skills_by_group,
    }

    return render(request, "league_manager/level_up.html", context)




def modify_player_old(request, player_id):
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
    scheduled_matches = Match.objects.filter(league=league, status="scheduled").order_by('-id')

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
        'scheduled_matches': scheduled_matches,
    }
    return render(request, 'league_manager/league_details.html', context)

def get_team_value(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    return JsonResponse({'team_value': team.get_total_team_value()})

def schedule_match(request, league_id):
    league = get_object_or_404(League, id=league_id)
    teams = Team.objects.filter(league=league)

    if request.method == 'POST':
        team1_id = request.POST.get('team1_id')
        team2_id = request.POST.get('team2_id')
        team1 = get_object_or_404(Team, id=team1_id)
        team2 = get_object_or_404(Team, id=team2_id)

        match = Match.objects.create(league=league, team1=team1, team2=team2)

        action = request.POST.get("action")
        
        if action == "schedule":
            
            return redirect('league_details', league_id=league_id)
        
        if action == "start":
            return redirect('start_match', match_id=match.id)

    context = {
        'league':league,
        'teams':teams,
    }

    return render(request, 'league_manager/schedule_match.html', context)


def start_match(request, match_id):

    match = get_object_or_404(Match, id=match_id)
    league = match.league

    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'start':
            match.team1_fame = request.POST.get('team1_fame')
            match.team1_fame = request.POST.get('team1_fame')
            match.weather = request.POST.get('weather_dropdown')
            match.status = 'in_progress'

            print(match.team1_fame)
            print(match.team2_fame)
            print(match.weather)
            print(match.status)
            match.save()

            return redirect('match_page', match_id = match_id)
        
        if action == 'cancel':

            match.delete()

            return redirect('league_details', league_id = league.id)
    
    team1 = match.team1
    team2 = match.team2

    team1_team_value = team1.get_total_team_value()
    team2_team_value = team2.get_total_team_value()
    if team1_team_value == team2_team_value:
        inducing_team = None
        inducement_value = 0
    elif team1_team_value < team2_team_value:
        inducing_team = team1
        inducement_value = team2_team_value - team1_team_value
    elif team2_team_value < team1_team_value:
        inducing_team = team2
        inducement_value = team1_team_value - team2_team_value

    context = {
        'league': league,
        'team1': team1,
        'team2': team2,
        'team1_team_value': team1_team_value,
        'team2_team_value': team2_team_value,
        'inducing_team': inducing_team,
        'inducement_value': inducement_value,
    }

    return render(request, 'league_manager/start_match.html', context)


def end_match(request, match_id):
    
    match = get_object_or_404(Match, id=match_id)
    team1 = match.team1
    team2 = match.team2
    if request.method == "POST":
        team1_winnings = int(request.POST.get('team1_winnings'))
        match.team1_winnings = team1_winnings
        match.team1.treasury += team1_winnings
        team2_winnings = int(request.POST.get('team2_winnings'))
        match.team2_winnings = team2_winnings
        match.team2.treasury += team2_winnings
        team1_mvp = get_object_or_404(Player, id=request.POST.get('team1_mvp_id'))
        team1_mvp_obj = MostValuablePlayer.objects.create(match=match, player=team1_mvp, team=team1_mvp.team)
        team2_mvp = get_object_or_404(Player, id=request.POST.get('team2_mvp_id'))
        team2_mvp_obj = MostValuablePlayer.objects.create(match=match, player=team2_mvp, team=team2_mvp.team)
        team1_fanfactor_change = int(request.POST.get('team1_fanfactor_change'))
        match.team1_fanfactor_change = team1_fanfactor_change
        team1.fan_factor += team1_fanfactor_change
        team2_fanfactor_change = int(request.POST.get('team2_fanfactor_change'))
        match.team2_fanfactor_change = team2_fanfactor_change
        team2.fan_factor += team2_fanfactor_change
        match.team1.players.filter(miss_next=True).update(miss_next=False)
        match.team2.players.filter(miss_next=True).update(miss_next=False)
        casualties = Casualty.objects.filter(match=match)
        for cas in casualties:
            cas.victim_player.miss_next=True
            cas.victim_player.save()
        team1.save()
        team2.save()
        match.status = "completed"
        match.save()

        return redirect('league_details', league_id=match.league.id)

    team1 = match.team1
    team2 = match.team2
    team1_players = team1.players.all()
    team2_players = team2.players.all()
    team1_score = match.get_score()[0]
    team2_score = match.get_score()[1]
    context = {"team1":team1,
               "team2":team2,
               "team1_players": team1_players,
               "team2_players": team2_players,
               "team1_score":team1_score,
               "team2_score":team2_score,
               }

    return render(request, 'league_manager/end_of_match.html', context)


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
    team1_injuries, team2_injuries = match.get_teams_injuries()
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
        'team1_injuries':team1_injuries,
        'team2_injuries':team2_injuries,
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
    players = team.players.all() 
    
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

def add_injury(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)
    injury_types = InjuryType.objects.all()

    players = team.players.all()

    if request.method == 'POST':
        injured_player_id = request.POST.get('injured_player_id')
        injured_player = get_object_or_404(Player, id=injured_player_id)
        injury_type_id = request.POST.get('injury_type_id')
        injury_type = get_object_or_404(InjuryType, id=injury_type_id)

        Injury.objects.create(match=match, player=injured_player, injury_type=injury_type)

        return redirect('match_page', match_id=match_id)
    
    context = {
        'team':team,
        'match':match,
        'players':players,
        'injury_types': injury_types
    }
    
    return render(request, 'league_manager/add_injury.html', context)