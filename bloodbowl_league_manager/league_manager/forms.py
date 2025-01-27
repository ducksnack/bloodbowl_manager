from django import forms
from .models import Team, Player, PlayerType, League

class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['name', 'managers']

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'coach', 'faction']

class ModifyPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'number', 'position', 'movement', 'strength', 'agility', 'armour', 'skills', 'value']

    miss_next = forms.BooleanField(required=False, label='Miss Next Game')

class AddPlayerForm(forms.Form):
    name = forms.CharField(max_length=100, label='Player Name')
    player_type = forms.ModelChoiceField(
        queryset=PlayerType.objects.none(),
        label='Player Type'
    )

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)  # Pass the team object when initializing the form
        super().__init__(*args, **kwargs)

        if team:
            # Filter player types to exclude those that exceed the max_quantity limit
            valid_player_types = PlayerType.objects.filter(
                faction=team.faction
            ).exclude(
                id__in=[
                    pt.id for pt in PlayerType.objects.filter(faction=team.faction)
                    if Player.objects.filter(team=team, player_type=pt).count() >= pt.max_quantity
                ]
            )

            self.fields['player_type'].queryset = valid_player_types
        else:
            self.fields['player_type'].queryset = PlayerType.objects.none()

        # Use position as the display label for dropdown options
        self.fields['player_type'].label_from_instance = lambda obj: obj.position

class ModifyTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['rerolls', 'apothecary', 'assistant_coaches', 'cheerleaders', 'fan_factor', 'treasury']

    apothecary = forms.BooleanField(required=False)  # This will be a checkbox