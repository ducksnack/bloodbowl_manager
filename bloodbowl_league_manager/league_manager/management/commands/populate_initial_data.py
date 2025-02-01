import json
import os
import re
from django.core.management.base import BaseCommand
from league_manager.models import PlayerType, Faction, InjuryType, LevelUpType, Skill
from django.shortcuts import get_object_or_404

class Command(BaseCommand):
    help = 'Populate database with initial data for player types, factions, injury types, and level-up types'
    
    def handle(self, *args, **kwargs):
        self.populate_skills()
        factions = self.populate_factions()
        self.populate_player_types(factions)
        self.populate_injury_types()
        self.populate_level_up_types()

        self.stdout.write(self.style.SUCCESS("All initial data populated successfully!"))

    def populate_factions(self):

        # Clear existing data
        Faction.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared all existing factions."))

        factions = [
            {"name": "Amazon", "reroll": 50, "apo": True},
            {"name": "Chaos Chosen", "reroll": 60, "apo": True},
            {"name": "Chaos Dwarf", "reroll": 70, "apo": True},
            {"name": "Chaos Renegade", "reroll": 70, "apo": True},
            {"name": "Dark Elf", "reroll": 50, "apo": True},
            {"name": "Dwarf", "reroll": 50, "apo": True},
            {"name": "Elven Union", "reroll": 50, "apo": True},
            {"name": "Goblin", "reroll": 60, "apo": True},
            {"name": "Halfling", "reroll": 60, "apo": True},
            {"name": "High Elf", "reroll": 50, "apo": True},
            {"name": "Human", "reroll": 50, "apo": True},
            {"name": "Lizardmen", "reroll": 60, "apo": True},
            {"name": "Necromantic Horror", "reroll": 70, "apo": False},
            {"name": "Norse", "reroll": 60, "apo": True},
            {"name": "Nurgle", "reroll": 70, "apo": False},
            {"name": "Ogre", "reroll": 70, "apo": True},
            {"name": "Old World Alliance", "reroll": 70, "apo": True},
            {"name": "Orc", "reroll": 60, "apo": True},
            {"name": "Shambling Undead", "reroll": 70, "apo": False},
            {"name": "Skaven", "reroll": 60, "apo": True},
            {"name": "Slann", "reroll": 50, "apo": True},
            {"name": "Snotling", "reroll": 50, "apo": True},
            {"name": "Tomb Kings", "reroll": 70, "apo": False},
            {"name": "Underworld Denizens", "reroll": 50, "apo": True},
            {"name": "Vampire", "reroll": 70, "apo": True},
            {"name": "Wood Elf", "reroll": 50, "apo": True},
        ]

        ICON_BASE_PATH = "league_manager/icons/"
        for faction in factions:
            formatted_name = faction["name"].lower().replace(" ", "-")  # Convert to lowercase and replace spaces with hyphens
            faction["icon"] = f"{ICON_BASE_PATH}{formatted_name}.png"

        for faction in factions:
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

        # Define the base path for icons
        ICON_BASE_PATH = "league_manager/icons/faction_postional_icons/"

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
        
            # Append the icon_path to each entry in player_types
            faction_name = pt["faction"].lower().replace(" ", "-")  # Convert to lowercase, replace spaces
            position_name = pt["position"].lower().replace(" ", "-")  # Convert position to lowercase, replace spaces
            pt["icon_path"] = f"{ICON_BASE_PATH}{faction_name}-{position_name}.png"

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
                double_skill_access = pt["double_skill_access"],
                icon_path=pt["icon_path"])
            
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
        skill_file_path = os.path.join(current_dir, "skill_descriptions.txt")

        # Ensure the file exists before proceeding
        if not os.path.exists(skill_file_path):
            print(f"Error: File not found -> {skill_file_path}")
        else:
            print(f"Succes: File found -> {skill_file_path}")
            with open(skill_file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()  # Read entire file

            # Split skills by line break (empty line)
            skills_data = content.split("\n\n")

            for skill_block in skills_data:
                # Match "Skill Name (Category)" pattern
                match = re.match(r"(.+?) \((.+?)\)\n(.+)", skill_block, re.DOTALL)
                if match:
                    name = match.group(1).strip()  # Skill name before parenthesis
                    category = match.group(2).strip()  # Category inside parenthesis
                    description = match.group(3).strip()  # Everything after category

                    # Save to database
                    obj, created = Skill.objects.get_or_create(
                        name=name, 
                        category=category, 
                        defaults={"description": description}
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added skill: {name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Skill already exists: {name}"))


