from django.core.management.base import BaseCommand
from league_manager.models import PlayerType, Faction, InjuryType
from django.shortcuts import get_object_or_404

class Command(BaseCommand):
    help = 'Populate database with initial data for player types, factions, and injury types'
    
    def handle(self, *args, **kwargs):
        self.populate_factions()
        self.populate_player_types()
        self.populate_injury_types()

        self.stdout.write(self.style.SUCCESS("All initial data populated successfully!"))

    def populate_factions(self):

        factions = [
            {"name": "Humans", "reroll": 50, "apo": True},
            {"name": "Wood Elves", "reroll": 50, "apo": True},
            {"name": "High Elves", "reroll": 50, "apo": True},
            {"name": "Amazons", "reroll": 50, "apo": True},
            {"name": "Chaos", "reroll": 60, "apo": True}
            # Add more factions here
        ]

        for faction in factions:
                obj, created = Faction.objects.get_or_create(faction_name=faction["name"], reroll_value=faction["reroll"], apo_available=faction["apo"])
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added faction: {faction['name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Faction already exists: {faction['name']}"))

    
    def populate_player_types(self):

        factions = {
            "Humans": get_object_or_404(Faction, faction_name="Humans"),
            "Amazons": get_object_or_404(Faction, faction_name="Amazons"),
        }

        player_types = [
            # {"name": "HumanLineman", "faction": factions["Humans"], "position": "Lineman", "max_quantity": 16, "price": 50, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "-", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "AmazonLinewoman", "faction": factions["Amazons"], "position": "Linewoman", "max_quantity": 16, "price": 50, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Dodge", "normal_skill_access": "G", "double_skill_access": "ASP"},
            # Add more player types here
        ]

        for pt in player_types:
            obj, created = PlayerType.objects.get_or_create(name=pt["name"], faction=pt["faction"], position=pt["position"], max_quantity=pt["max_quantity"], price=pt["price"], movement=pt["movement"], strength=pt["strength"], agility=pt["agility"], armour=pt["armour"], starting_skills=pt["starting_skills"], normal_skill_access=pt["normal_skill_access"], double_skill_access=pt["double_skill_access"])
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

    