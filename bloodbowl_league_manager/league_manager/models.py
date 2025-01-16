from django.db import models
from django.contrib.auth.models import User

class League(models.Model):
    name = models.CharField(max_length=100)
    managers = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Faction(models.Model):
    faction_name = models.CharField(max_length=100)
    reroll_value = models.IntegerField()
    apo_available = models.BooleanField(default=True)

    def __str__(self):
        return self.faction_name
    
class Team(models.Model):
    name = models.CharField(max_length=100)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE, null=True, blank=True)
    coach = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.SET_NULL, null=True, blank=True)
    rerolls = models.IntegerField(default=0)
    apothecary = models.BooleanField(default=False)
    assistant_coaches = models.IntegerField(default=0)
    cheerleaders = models.IntegerField(default=0)
    fan_factor = models.IntegerField(default=0)
    treasury = models.IntegerField(default=0)

    def get_total_team_value(self):
        total_team_value = sum(player.value for player in self.players.all())
        total_team_value += self.faction.reroll_value*self.rerolls
        total_team_value += 50*self.apothecary
        total_team_value += 10*self.assistant_coaches
        total_team_value += 10*self.cheerleaders
        total_team_value += 10*self.fan_factor

        return total_team_value

    
    def __str__(self):
        return self.name

class PlayerType(models.Model):
    name = models.CharField(max_length=100)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE, related_name='player_types')
    position = models.CharField(max_length=100)
    max_quantity = models.IntegerField()
    price = models.IntegerField()
    movement = models.IntegerField()
    strength = models.IntegerField()
    agility = models.IntegerField()
    armour = models.IntegerField()
    starting_skills = models.CharField(max_length=100)
    normal_skill_access = models.CharField(max_length=100)
    double_skill_access = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Player(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Retired', 'Retired'),
        ('Dead', 'Dead'),
    ]

    name = models.CharField(max_length=100, default='None')
    number = models.IntegerField()
    player_type = models.ForeignKey(PlayerType, on_delete=models.CASCADE, related_name='players', null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players', null=True)
    position = models.CharField(max_length=100, default='None')
    value = models.IntegerField(default=0)
    movement = models.IntegerField(default=0)
    strength = models.IntegerField(default=0)
    agility = models.IntegerField(default=0)
    armour = models.IntegerField(default=0)
    skills = models.CharField(max_length=100, default='None')
    normal_skill_access = models.CharField(max_length=100, default='None')
    double_skill_access = models.CharField(max_length=100, default='None')
    injuries = models.CharField(max_length=100, default='None')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active',
    )
    miss_next = models.BooleanField(default=False)
    injuries = models.CharField(max_length=100, default="")
    # pass_completions = models.IntegerField(default=0)
    # touchdowns = models.IntegerField(default=0)
    # interceptions = models.IntegerField(default=0)
    # casualties = models.IntegerField(default=0)
    # mvps = models.IntegerField(default=0)

    def get_n_completions(self):
        n_pcs = self.thrower_completions.filter(match__status="completed").count()
        return n_pcs
    
    def get_n_touchdowns(self):
        n_tds = self.player_touchdowns.filter(match__status="completed").count()
        return n_tds
    
    def get_n_casualties(self):
        n_cas = self.caused_casualties.filter(match__status="completed").count()
        return n_cas
    
    def get_n_interceptions(self):
        n_int = self.caught_interceptions.filter(match__status="completed").count()
        return n_int
    
    def get_n_mvps(self):
        n_mvps =  self.player_mvps.filter(match__status="completed").count()
        return n_mvps
    
    """
    def initialize_stats_from_player_type(self):
        # Sets initial stats based on the associated PlayerType.
        self.position = self.player_type.position
        self.value = self.player_type.price
        self.strength = self.player_type.strength
        self.agility = self.player_type.agility
        self.movement = self.player_type.movement
        self.armour = self.player_type.armour
        self.skills = self.player_type.starting_skills
        self.normal_skill_access = self.player_type.normal_skill_access
        self.double_skill_access = self.player_type.double_skill_access
    """
    def calculate_spp(self):
        spp = 1 * self.get_n_completions() + 3 * self.get_n_touchdowns() + 2 * self.get_n_interceptions() + 2 * self.get_n_casualties() + 5 * self.get_n_mvps()
        return spp
    """
    def save(self, *args, **kwargs):
        # Ensure the stats are initialized from player_type before saving
        self.initialize_stats_from_player_type()
        
        super().save(*args, **kwargs)
    """
    def __str__(self):
        return self.name
    
class Match(models.Model):

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('invalid', 'Invalid'),
    ]

    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='matches')
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    status = models.CharField(max_length=15,
                              choices=STATUS_CHOICES,
                              default='in_progress')
    
    def get_teams_completions(self):
        team1_comps = self.match_completions.filter(team=self.team1)
        team2_comps = self.match_completions.filter(team=self.team2)

        return [team1_comps, team2_comps]

    def get_teams_tds(self):
        team1_tds = self.match_touchdowns.filter(team=self.team1)
        team2_tds = self.match_touchdowns.filter(team=self.team2)

        return [team1_tds, team2_tds]
    
    def get_teams_casualties(self):
        team1_cas = self.match_casualties.filter(causing_team=self.team1)
        team2_cas = self.match_casualties.filter(causing_team=self.team2)

        return [team1_cas, team2_cas]
    
    def get_score(self):
        team1_score = self.get_teams_tds()[0].count()
        team2_score = self.get_teams_tds()[1].count()

        return [team1_score, team2_score]
    
    def get_result(self):
        score = self.get_score()
        if score[0] > score[1]:
            result = self.team1.name
        elif score[0] < score[1]:
            result = self.team2.name
        else:
            result = 'draw'

        return result


class Touchdown(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_touchdowns')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_touchdowns')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_touchdowns', null=True)

class PassCompletion(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_completions')
    thrower = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='thrower_completions')
    receiver = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='receiver_completions')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_completions', null=True)

class Casualty(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_casualties')
    causing_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='caused_casualties')
    victim_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='suffered_casualties')
    causing_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='casualties_inflicted', null=True)
    victim_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='casualties_sustained', null=True)

class Interception(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_interceptions')
    intercepting_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='caught_interceptions')
    throwing_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='thrown_interceptions')
    intercepting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_caught_interceptions', null=True)
    throwing_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_thrown_interceptions', null=True)

class MostValuablePlayer(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_mvps')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_mvps')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_mvps', null=True)