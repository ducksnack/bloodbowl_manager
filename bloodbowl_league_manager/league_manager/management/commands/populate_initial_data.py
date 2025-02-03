import csv
import json
import os
import re
from django.core.management.base import BaseCommand
from league_manager.models import Casualty, Interception, League, Match, MostValuablePlayer, PassCompletion, Player, PlayerType, Faction, InjuryType, LevelUpType, Skill, Team, Touchdown
from django.shortcuts import get_object_or_404

class Command(BaseCommand):
    help = 'Populate database with initial data for player types, factions, injury types, and level-up types'
    
    #Hardcoded league name, for creating our current league. Placed here so it is easy to change
    league_name = "Horsens Noob-League"
    
    def handle(self, *args, **kwargs):
        self.populate_skills()
        factions = self.populate_factions()
        self.populate_player_types(factions)
        self.populate_injury_types()
        self.populate_level_up_types()
        self.create_our_league()
        self.import_team_from_csv("A-mice-ing_Critters.csv")
        self.import_team_from_csv("Pyramid_Schemers.csv")
        self.import_team_from_csv("Leafy_Greens.csv")
        self.import_team_from_csv("Puny_Humans.csv")
        self.import_team_from_csv("OK_Øgle.csv")
        self.import_team_from_csv("The_Lushy_Legends.csv")
        self.recreate_match_history("match1.json")
        self.recreate_match_history("match2.json")
        self.recreate_match_history("match3.json")
        self.recreate_match_history("match4.json")

        self.stdout.write(self.style.SUCCESS("All initial data populated successfully!"))

    def create_our_league(self):
        League.objects.all().delete()
        created = League.objects.create(
                name=self.league_name, 
                managers="Michael", 
                current = True
            )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Added league: {created.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"League was not created: {created.name}"))

    def recreate_match_history(self, match):
        
        # Get the directory of the current script (populate_initial_data.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full file path
        DATA_FILE = os.path.join(current_dir, match)

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                match = json.load(file)

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("Error: skills.json file not found."))
            return

        created_match = Match.objects.create(
            league = League.objects.get(name=self.league_name),
            team1 = Team.objects.get(name=match["match"]["team_1"]["name"]),
            team2 = Team.objects.get(name=match["match"]["team_2"]["name"]),
            team1_fame=match["match"]["team_1"]["FAME"],
            team2_fame=match["match"]["team_2"]["FAME"],
            weather=match["match"]["weather"],
            team1_winnings=match["match"]["team_1"]["Winnings"],
            team2_winnings=match["match"]["team_2"]["Winnings"],
            team1_fanfactor_change=match["match"]["team_1"]["FF_change"],
            team2_fanfactor_change=match["match"]["team_2"]["FF_change"],
            status=match["match"]["status"]
        )

        team1_pass_completions = match["match"]["team_1"]["PC"]
        team2_pass_completions = match["match"]["team_2"]["PC"]

        for pc in team1_pass_completions:
            PassCompletion.objects.create(
                match=created_match,
                thrower=Player.objects.get(team=created_match.team1, number=pc),
                receiver=Player.objects.get(team=created_match.team1, number=pc), #Throws to himself for now, since we dont have this tracked in our historic data
                team=created_match.team1
            )

        for pc in team2_pass_completions:
            PassCompletion.objects.create(
                match=created_match,
                thrower=Player.objects.get(team=created_match.team2, number=pc),
                receiver=Player.objects.get(team=created_match.team2, number=pc), #Throws to himself for now, since we dont have this tracked in our historic data
                team=created_match.team2
            )

        team1_touchdowns = match["match"]["team_1"]["TD"]
        team2_touchdowns = match["match"]["team_2"]["TD"]

        for td in team1_touchdowns:
            Touchdown.objects.create(
                match=created_match,
                player=Player.objects.get(team=created_match.team1, number=td),
                team=created_match.team1
            )

        for td in team2_touchdowns:
            Touchdown.objects.create(
                match=created_match,
                player=Player.objects.get(team=created_match.team2, number=td),
                team=created_match.team2
            )

        team1_interceptions = match["match"]["team_1"]["INT"]
        team2_interceptions = match["match"]["team_2"]["INT"]

        for int in team1_interceptions:
            Interception.objects.create(
                match=created_match,
                intercepting_player=Player.objects.get(team=created_match.team1, number=int),
                throwing_player=Player.objects.get(team=created_match.team1, number=int), #Intercepts himself for now, since we dont have this tracked in our historic data
                intercepting_team=created_match.team1,
                throwing_team=created_match.team2
            )

        for int in team2_interceptions:
            Interception.objects.create(
                match=created_match,
                intercepting_player=Player.objects.get(team=created_match.team2, number=int),
                throwing_player=Player.objects.get(team=created_match.team2, number=int), #Intercepts himself for now, since we dont have this tracked in our historic data
                intercepting_team=created_match.team2,
                throwing_team=created_match.team1
            )

        team1_casualties = match["match"]["team_1"]["CAS"]
        team2_casualties = match["match"]["team_2"]["CAS"]
        
        for cas in team1_casualties:
            Casualty.objects.create(
                match=created_match,
                causing_player=Player.objects.get(team=created_match.team1, number=cas),
                victim_player=Player.objects.get(team=created_match.team1, number=cas), #Casualties himself for now, since we dont have this tracked in our historic data
                causing_team=created_match.team1,
                victim_team=created_match.team2
            )

        for cas in team2_casualties:
            Casualty.objects.create(
                match=created_match,
                causing_player=Player.objects.get(team=created_match.team2, number=cas),
                victim_player=Player.objects.get(team=created_match.team2, number=cas), #Casualties himself for now, since we dont have this tracked in our historic data
                causing_team=created_match.team2,
                victim_team=created_match.team1
            )

        team1_mvp = match["match"]["team_1"]["MVP"]
        team2_mvp = match["match"]["team_2"]["MVP"]

        if team1_mvp > 0:
            MostValuablePlayer.objects.create(
                match=created_match,
                player=Player.objects.get(team=created_match.team1, number=team1_mvp),
                team=created_match.team1
            )

        if team2_mvp > 0:
            MostValuablePlayer.objects.create(
                match=created_match,
                player=Player.objects.get(team=created_match.team2, number=team2_mvp),
                team=created_match.team2
            )

        if created_match:
            self.stdout.write(self.style.SUCCESS(f"Added match: {created_match.team1.name} - {created_match.team2.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Could not add match: {created_match.team1.name} - {created_match.team2.name}")) 

    def populate_factions(self):

        # Clear existing data
        Faction.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared all existing factions."))

        # Define the base path for icons
        ICON_BASE_PATH = "images/icons_factions/"

        # Get the directory of the current script (populate_initial_data.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full file path
        DATA_FILE = os.path.join(current_dir, "factions.json")

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                factions = json.load(file)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("Error: player_types.json file not found."))
            return

        for faction in factions:
            formatted_name = faction["name"].lower().replace(" ", "-")  # Convert to lowercase and replace spaces with hyphens
            faction["icon"] = f"{ICON_BASE_PATH}{formatted_name}.png"
            
            obj, created = Faction.objects.get_or_create(
                faction_name=faction["name"], 
                reroll_value=faction["reroll"], 
                apo_available=faction["apo"],
                icon_path=faction["icon"]
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added faction: {faction['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Faction already exists: {faction['name']}"))
    
        return factions

    
    def populate_player_types(self, factions_list):

        # Clear existing data
        PlayerType.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared all existing player types."))

        # Mapping skill category abbreviations to full names
        SKILL_CATEGORY_MAP = {
            "G": "General",
            "A": "Agility",
            "S": "Strength",
            "P": "Passing",
            "M": "Mutation",
            "E": "Extraordinary",
        }

        # Get the directory of the current script (populate_initial_data.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full file path
        DATA_FILE = os.path.join(current_dir, "rosters.json")

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                player_types = json.load(file)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("Error: player_types.json file not found."))
            return

        for pt in player_types:

            # Get Faction object
            faction_obj = Faction.objects.get(faction_name=pt["faction"])
        
            obj, created = PlayerType.objects.get_or_create(
                name=pt["name"], 
                faction=faction_obj, 
                position=pt["position"], 
                max_quantity=pt["max_quantity"], 
                price=pt["price"], 
                movement=pt["movement"], 
                strength=pt["strength"], 
                agility=pt["agility"], 
                armour=pt["armour"],
                normal_skill_access=pt["normal_skill_access"],
                double_skill_access = pt["double_skill_access"]
                )
            
            starting_skills_str = pt["starting_skills"]
            if starting_skills_str and starting_skills_str != "-":
                
                # Split the string on commas and strip any extra whitespace
                skill_names = [skill.strip() for skill in starting_skills_str.split(",")]
                
                # For each skill name, get (or create) the Skill object and add it to the m2m field
                for skill_name in skill_names:
                    try:
                        # Adjust the lookup field to match your Skill model definition
                        skill_obj = Skill.objects.get(name=skill_name)
                    except Exception as e:
                        print(f"Error retrieving or creating skill '{skill_name}': {e}")
                        continue

                    # Add the skill to the player_type_obj many-to-many field.
                    # Make sure the player_type_obj is saved first.
                    obj.starting_skills.add(skill_obj)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added player type: {pt['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Player type already exists: {pt['name']}"))

    
    def populate_injury_types(self):
        injury_types = [
            {"name": "Badly Hurt", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "No long term effect"},
            {"name": "Broken Ribs", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Groin Strain", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Gouged Eye", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Broken Jaw", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Fractured Arm", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Fractured Leg", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Smashed Hand", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Pinched Nerve", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Miss next game"},
            {"name": "Damaged Back", "niggling": True, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Niggling"},
            {"name": "Smashed Knee", "niggling": True, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "Niggling"},
            {"name": "Smashed Hip", "niggling": False, "ma_modifier": -1, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "-MA"},
            {"name": "Smashed Ankle", "niggling": False, "ma_modifier": -1, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "-MA"},
            {"name": "Serious Concussion", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": -1, "dead": False, "description": "-AV"},
            {"name": "Fractured Skull", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": -1, "dead": False, "description": "-AV"},
            {"name": "Broken Neck", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": -1, "av_modifier": 0, "dead": False, "description": "-AG"},
            {"name": "Smashed Collar Bone", "niggling": False, "ma_modifier": 0, "st_modifier": -1, "ag_modifier": 0, "av_modifier": 0, "dead": False, "description": "-ST"},
            {"name": "Dead", "niggling": False, "ma_modifier": 0, "st_modifier": 0, "ag_modifier": 0, "av_modifier": 0, "dead": True, "description": "Dead"},
            # Add more injury types here
        ]

        for it in injury_types:
            obj, created = InjuryType.objects.get_or_create(name=it["name"], ma_modifier=it["ma_modifier"], st_modifier=it["st_modifier"], ag_modifier=it["ag_modifier"], av_modifier=it["av_modifier"], dead=it["dead"], description=it["description"])
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added injury type: {it['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Injury type already exists: {it['name']}"))

    def populate_level_up_types(self):

        level_up_types = [
            # General Skills
            {'name':'Block', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill':'Block', 'category':'G'},
            {'name':'Dauntless', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill':'Dauntless', 'category':'G'},
            {'name':'Dirty Player', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill':'Dirty Player', 'category':'G'},
            {'name':'Fend', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill':'Fend', 'category':'G'},
            {'name':'Frenzy', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill':'Frenzy', 'category':'G'},
            {'name':'Kick', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Kick', 'category':'G'},
            {'name':'Kick-off Return', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Kick-off Return', 'category':'G'},
            {'name':'Pass Block', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Pass Block', 'category':'G'},
            {'name':'Pro', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Pro', 'category':'G'},
            {'name':'Shadowing', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Shadowing', 'category':'G'},
            {'name':'Strip Ball', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Strip Ball', 'category':'G'},
            {'name':'Sure Hands', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Sure Hands', 'category':'G'},
            {'name':'Tackle', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Tackle', 'category':'G'},
            {'name':'Wrestle', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Wrestle', 'category':'G'},
            # Agility
            {'name':'Catch', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Catch', 'category':'A'},
            {'name':'Diving Catch', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Diving Catch', 'category':'A'},
            {'name':'Diving Tackle', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Diving Tackle', 'category':'A'},
            {'name':'Dodge', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Dodge', 'category':'A'},
            {'name':'Jump Up', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Jump Up', 'category':'A'},
            {'name':'Leap', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Leap', 'category':'A'},
            {'name':'Side Step', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Side Step', 'category':'A'},
            {'name':'Sneaky Git', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Sneaky Git', 'category':'A'},
            {'name':'Sprint', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Sprint', 'category':'A'},
            {'name':'Sure Feet', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Sure Feet', 'category':'A'},
            # Strength
            {'name':'Break Tackle', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Break Tackel', 'category':'S'},
            {'name':'Grab', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Grab', 'category':'S'},
            {'name':'Guard', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Guard', 'category':'S'},
            {'name':'Juggernaut', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Juggernaut', 'category':'S'},
            {'name':'Mighty Blow', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Mightny Blow', 'category':'S'},
            {'name':'Multiple Block', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Multiple Block', 'category':'S'},
            {'name':'Piling On', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Piling On', 'category':'S'},
            {'name':'Stand Firm', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Stand Firm', 'category':'S'},
            {'name':'Strong Arm', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Strong Arm', 'category':'S'},
            {'name':'Thick Skull', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Thick Skull', 'category':'S'},
            # Passing
            {'name':'Accurate', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Accurate', 'category':'P'},
            {'name':'Dump-off', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Dump-off', 'category':'P'},
            {'name':'Hail Mary Pass', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Hail Mary Pass', 'category':'P'},
            {'name':'Leader', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Leader', 'category':'P'},
            {'name':'Nerves of Steel', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Nerves of Steel', 'category':'P'},
            {'name':'Pass', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Pass', 'category':'P'},
            {'name':'Safe Throw', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Safe Throw', 'category':'P'},
            # Mutation
            {'name':'Big Hand', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Big Hand', 'category':'M'},
            {'name':'Claw / Claws', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Claw / Claws', 'category':'M'},
            {'name':'Disturbing Presence', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Disturbing Presence', 'category':'M'},
            {'name':'Extra Arm', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Extra Arm', 'category':'M'},
            {'name':'Foul Appearance', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill':'Foul Appearance', 'category':'M'},
            {'name':'Horns', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Horns', 'category':'M'},
            {'name':'Prehensile Tail', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Prehensile Tail', 'category':'M'},
            {'name':'Tentacles', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Tentacles', 'category':'M'},
            {'name':'Two Heads', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Two Heads', 'category':'M'},
            {'name':'Very Long Legs', 'ma':0, 'st':0, 'ag':0, 'av':0, 'skill': 'Very Long Legs', 'category':'M'},
            # Stat Increases
            {'name':'+ MA', 'ma':1, 'st':0, 'ag':0, 'av':0, 'skill': None, 'category':'+MA'},
            {'name':'+ ST', 'ma':0, 'st':1, 'ag':0, 'av':0, 'skill': None, 'category':'+ST'},
            {'name':'+ AG', 'ma':0, 'st':0, 'ag':1, 'av':0, 'skill': None, 'category':'+AG'},
            {'name':'+ AV', 'ma':0, 'st':0, 'ag':0, 'av':1, 'skill': None, 'category':'+AV'},
        ]

        for level_up_type in level_up_types:
            obj, created = LevelUpType.objects.get_or_create(name=level_up_type["name"], ma_modifier=level_up_type["ma"], st_modifier=level_up_type["st"], ag_modifier=level_up_type["ag"], av_modifier=level_up_type["av"], skill=level_up_type["skill"], category=level_up_type["category"])
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added level-up type: {level_up_type['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Level-up type already exists: {level_up_type['name']}"))

    def populate_skills(self):

        # Clear existing data
        Skill.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared all existing skills."))

        # Get the directory of the current script (populate_initial_data.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full file path
        DATA_FILE = os.path.join(current_dir, "skills.json")

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                skills = json.load(file)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("Error: skills.json file not found."))
            return
        
        for skill in skills:
            obj, created = Skill.objects.get_or_create(
                    name=skill["name"], 
                    category=skill["category"], 
                    description=skill["description"]
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added skill: {skill['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skill already exists: {skill['name']}")) 

    def import_team_from_csv(self, file_path):

        # Get the directory of the current script (populate_initial_data.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full file path
        DATA_FILE = os.path.join(current_dir, file_path)

        # Read all rows from the CSV file
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        # --- Extract Team Info ---
        team_name = rows[0][3]
        team_faction_name = rows[1][3]
        team_coach = rows[1][10]

        # --- Lookup Faction ---
        faction = Faction.objects.filter(faction_name__iexact=team_faction_name).first()
        if not faction:
            print(f"❌ Error: Faction '{team_faction_name}' not found!")
            return  # Stop if faction doesn’t exist
        
        # --- Lookup League ---
        league = League.objects.filter(name__iexact=self.league_name).first()

        # --- Extract Team Assets ---
        team_rerolls = int(rows[22][3]) if rows[22][3].strip() else 0
        assistant_coaches = int(rows[22][9]) if rows[22][9].strip() else 0
        treasury = int(rows[22][13]) if rows[22][13].strip() else 0
        cheerleaders = int(rows[23][9]) if rows[23][9].strip() else 0
        apothecary_status = rows[24][3].strip().lower() == "yes"  # True if "yes", False otherwise
        fan_factor = int(rows[24][9]) if rows[24][9].strip() else 0

        # --- Create the Team ---
        team = Team.objects.create(
            name=team_name,
            faction=faction,
            coach=team_coach,
            rerolls=team_rerolls,
            assistant_coaches=assistant_coaches,
            treasury=treasury,
            cheerleaders=cheerleaders,
            apothecary=apothecary_status,
            fan_factor=fan_factor,
            league=league
        )

        print(f"✅ Created Team: {team.name} ({team.faction})")

        # --- Extract Player Info ---
        header = rows[3]  # The CSV header row
        header_mapping = {col.strip(): i for i, col in enumerate(header) if col.strip()}

        for row in rows[4:20]:  # Loop over player rows
            if not any(row) or not row[0].strip().isdigit():
                continue  # Skip empty rows

            # --- Extract Player Data ---
            player_number = int(row[header_mapping.get("#", 0)].strip())
            player_name = row[header_mapping.get("Name", 1)].strip()
            position = row[header_mapping.get("Position", 5)].strip()
            movement = int(row[header_mapping.get("MA", 10)].strip())
            strength = int(row[header_mapping.get("ST", 11)].strip())
            agility = int(row[header_mapping.get("AG", 12)].strip())
            armour = int(row[header_mapping.get("AV", 13)].strip())
            skills_string = row[header_mapping.get("Skills", 14)].strip()
            skills_list = [s.strip() for s in skills_string.split(",") if s.strip()]

            level = int(row[header_mapping.get("Lvl", 32)].strip()) if row[header_mapping.get("Lvl", 32)].strip() else 0
            value = int(row[header_mapping.get("Value", 33)].strip()) if row[header_mapping.get("Value", 33)].strip() else 0

            # --- Lookup or Create PlayerType ---
            player_type = PlayerType.objects.filter(faction=faction, position__iexact=position).first()
            if not player_type:
                print(f"❌ Warning: No PlayerType found for {faction} - {position}, skipping player {player_name}.")
                continue  # Skip player if no PlayerType exists

            # --- Create Player ---
            player = Player.objects.create(
                name=player_name,
                number=player_number,
                position=position,
                movement=movement,
                strength=strength,
                agility=agility,
                armour=armour,
                level=level,
                value=value,
                team=team,
                player_type=player_type,
                normal_skill_access=player_type.normal_skill_access,
                double_skill_access=player_type.double_skill_access,
                injuries="None",
                status="Active",
                miss_next=False,
            )

            # --- Assign Skills ---
            for skill_name in skills_list:
                skill = Skill.objects.filter(name__iexact=skill_name).first()
                if skill:
                    player.skills.add(skill)
                else:
                    print(f"⚠️ Warning: Skill '{skill_name}' not found for player {player_name}.")

            print(f"✅ Created Player: {player.name} ({player.position}) for {team.name}")

        print("✅ Import Complete!")
