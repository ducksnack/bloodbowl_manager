from django.db import models
from django.contrib.auth.models import User
from bisect import bisect_right

class League(models.Model):
    name = models.CharField(max_length=100)
    managers = models.CharField(max_length=100)
    current = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Faction(models.Model):
    faction_name = models.CharField(max_length=100)
    reroll_value = models.IntegerField()
    apo_available = models.BooleanField(default=True)
    icon_path = models.CharField(max_length=255, blank=True)


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
    normal_skill_access = models.CharField(max_length=10)
    double_skill_access = models.CharField(max_length=10)

     # Many-to-Many relationships with Skill
    starting_skills = models.ManyToManyField('Skill', related_name='starting_skill_players')

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
    skills = models.ManyToManyField('Skill', related_name='skill_players')
    level = models.IntegerField(default=0)
    normal_skill_access = models.CharField(max_length=10, default='None')
    double_skill_access = models.CharField(max_length=10, default='None')
    injuries = models.CharField(max_length=100, default='None')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active',
    )
    miss_next = models.BooleanField(default=False)

    def set_starting_attributes(self):
        self.skills.set(self.player_type.starting_skills.all())
        self.movement = self.player_type.movement
        self.strength = self.player_type.strength
        self.agility = self.player_type.agility
        self.armour = self.player_type.armour
        self.value = self.player_type.price
        self.position = self.player_type.position
        self.save()

    def get_injuries(self):
        injuries = self.player_injuries.filter(match__status="completed")
        return injuries

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
    
    def calculate_spp(self):
        spp = 1 * self.get_n_completions() + 3 * self.get_n_touchdowns() + 2 * self.get_n_interceptions() + 2 * self.get_n_casualties() + 5 * self.get_n_mvps()
        return spp
    
    def get_level_ups(self):
        level_ups = self.level_ups.all()
        return level_ups

    def get_stat_increases(self):
        return StatIncrease.objects.filter(levelup__player=self)

    def get_gained_skills(self):
        return Skill.objects.filter(levelup__player=self)

    def get_stats(self):
        base_ma = self.movement
        base_st = self.strength
        base_ag = self.agility
        base_av = self.armour
        ma_modifier = 0
        st_modifier = 0
        ag_modifier = 0
        av_modifier = 0
        stat_increases = self.get_stat_increases()
        for stat_increase in stat_increases:
            ma_modifier += stat_increase.ma_modifier
            st_modifier += stat_increase.st_modifier
            ag_modifier += stat_increase.ag_modifier
            av_modifier += stat_increase.av_modifier
        injuries = self.get_injuries()
        for injury in injuries:
            ma_modifier += injury.injury_type.ma_modifier
            st_modifier += injury.injury_type.st_modifier
            ag_modifier += injury.injury_type.ag_modifier
            av_modifier += injury.injury_type.av_modifier

        ma = base_ma + ma_modifier
        st = base_st + st_modifier
        ag = base_ag + ag_modifier
        av = base_av + av_modifier

        return {"movement":ma, "strength":st, "agility":ag, "armour":av}
    
    def get_skill_list(self):
        return self.skills.all() | self.get_gained_skills()
    
    def get_value(self):
        skill_dict = {
            'General':'G',
            'Agility':'A',
            'Strength':'S',
            'Passing':'P',
            'Mutation':'M',
        }

        value = self.value
        gained_skills = self.get_gained_skills()
        for skill in gained_skills:
            if skill_dict[skill.category] in self.normal_skill_access:
                value +=20
            if skill_dict[skill.category] in self.double_skill_access:
                value +=30
        stat_increases = self.get_stat_increases()
        for stat_increase in stat_increases:
            value += stat_increase.value
        return value

    def get_expected_level(self):
        level_thresholds = [(0, 0), (6, 1), (16, 2), (31, 3)]

        index = bisect_right([threshold[0] for threshold in level_thresholds], self.calculate_spp())
        return level_thresholds[index - 1][1]
    
    def get_level(self):
        return self.level_ups.count()
    
    def can_level_up(self):
        if self.get_expected_level() > self.get_level():
            return True
        else:
            return False


    def __str__(self):
        return self.name
    
class Match(models.Model):

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('scheduled', 'Scheduled'),
        ('invalid', 'Invalid'),
    ]

    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='matches')
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    team1_fame = models.IntegerField(default=0)
    team2_fame = models.IntegerField(default=0)
    weather = models.CharField(max_length=20, default="nice")
    team1_winnings = models.IntegerField(default=0)
    team2_winnings = models.IntegerField(default=0)
    team1_fanfactor_change = models.IntegerField(default=0)
    team2_fanfactor_change = models.IntegerField(default=0)
    status = models.CharField(max_length=15,
                              choices=STATUS_CHOICES,
                              default='scheduled') # a match should either be: in_progress, scheduled, completed, or invalid
    
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
    
    def get_teams_injuries(self):
        team1_injuries = self.match_injuries.filter(player__team=self.team1)
        team2_injuries = self.match_injuries.filter(player__team=self.team2)

        return [team1_injuries, team2_injuries]
    
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

class InjuryType(models.Model):
    name = models.CharField(max_length=25)
    niggling = models.BooleanField(default=False)
    ma_modifier = models.IntegerField(default=0)
    st_modifier = models.IntegerField(default=0)
    ag_modifier = models.IntegerField(default=0)
    av_modifier = models.IntegerField(default=0)
    dead = models.BooleanField(default=False)
    description = models.CharField(max_length=20, default="-")

    def __str__(self):
        return f'{self.name} [{self.description}]'

class Injury(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="match_injuries")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_injuries")
    injury_type = models.ForeignKey(InjuryType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.player} ({self.player.team}), {self.injury_type}'

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, default="")
    description = models.TextField()
    

    def __str__(self):
        return self.name

class StatIncrease(models.Model):
    name = models.CharField(max_length=25, default="stat_increase")
    value = models.IntegerField(default=0)
    ma_modifier = models.IntegerField(default=0)
    st_modifier = models.IntegerField(default=0)
    ag_modifier = models.IntegerField(default=0)
    av_modifier = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class LevelUp(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='level_ups')
    level_number = models.IntegerField(default=0)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, blank=True, null=True, default=None)
    stat_increase = models.ForeignKey(StatIncrease, on_delete=models.CASCADE, blank=True, null=True, default=None)

    def __str__(self):
        if self.skill:
            return f'{self.player}: {self.skill}'
        elif self.stat_increase:
            return f'{self.player}: {self.stat_increase}'
        else:
            return f'{self.player}: level up'
