from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('teams/', views.teams, name='teams'),
    path('create-team/', views.create_team, name='create_team'),
    path("team/<int:team_id>/", views.team_details, name="team_details"),
    path('player/<int:player_id>/modify/', views.modify_player, name='modify_player'),
    path('team/<int:team_id>/add_player/', views.add_player, name='add_player'),
    path('player/<int:player_id>/remove/', views.remove_player, name='remove_player'),
    path('team/<int:team_id>/modify/', views.modify_team, name='modify_team'),
    path('leagues/', views.league_list, name='leagues'),
    path('leagues/<int:league_id>/', views.league_details, name='league_details'),
    path('leagues/<int:league_id>/add_match/', views.add_match, name='add_match'),
    path('leagues/start_match/<int:league_id>/<int:team1_id>/<int:team2_id>/', views.start_match, name='start_match'),
    path('matches/<int:match_id>/', views.match_page, name='match_page'),
    path('add_touchdown/<int:match_id>/<int:team_id>/', views.add_touchdown, name='add_touchdown'),
    path('end_match/<int:match_id>/', views.end_match, name='end_match'),
    path('cancel_match/<int:match_id>/', views.cancel_match, name='cancel_match'),
    path('add_completion/<int:match_id>/<int:team_id>/', views.add_completion, name='add_completion'),
    path('add_casualty/<int:match_id>/<int:team_id>/', views.add_casualty, name='add_casualty'),
    path('add_interception/<int:match_id>/<int:team_id>/', views.add_interception, name='add_interception'),
    path('teams/<int:team_id>/get_team_value/', views.get_team_value, name='get_team_value'),
]