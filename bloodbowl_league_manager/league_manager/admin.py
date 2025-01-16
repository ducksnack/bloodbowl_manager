from django.contrib import admin
from .models import League, Team, Player, PlayerType, Faction, Match, Touchdown

admin.site.register(League)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(PlayerType)
admin.site.register(Faction)
admin.site.register(Match)
admin.site.register(Touchdown)