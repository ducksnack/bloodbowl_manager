import os
import re
from django.core.management.base import BaseCommand
from league_manager.models import PlayerType, Faction, InjuryType, LevelUpType, Skill
from django.shortcuts import get_object_or_404

class Command(BaseCommand):
    help = 'Populate database with initial data for player types, factions, injury types, and level-up types'
    
    def handle(self, *args, **kwargs):
        factions = self.populate_factions()
        self.populate_player_types(factions)
        self.populate_injury_types()
        self.populate_level_up_types()
        self.populate_skills()

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

        # Dynamically generate dictionary of faction objects
        factions = {faction["name"]: get_object_or_404(Faction, faction_name=faction["name"]) for faction in factions_list}

        player_types = [
            # Amazon
            {"name": "AmazonLinewoman", "faction": factions["Amazon"], "position": "Linewoman", "max_quantity": 16, "price": 50, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Dodge", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "AmazonThrower", "faction": factions["Amazon"], "position": "Thrower", "max_quantity": 2, "price": 70, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Dodge, Pass", "normal_skill_access": "GP", "double_skill_access": "AS"},
            {"name": "AmazonCatcher", "faction": factions["Amazon"], "position": "Catcher", "max_quantity": 2, "price": 70, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Dodge, Catch", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "AmazonBlitzer", "faction": factions["Amazon"], "position": "Blitzer", "max_quantity": 4, "price": 90, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Dodge, Block", "normal_skill_access": "GS", "double_skill_access": "AP"},
            # Chaos Chosen
            {"name": "ChaosBeastman", "faction": factions["Chaos Chosen"], "position": "Beastman", "max_quantity": 16, "price": 60, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Horns", "normal_skill_access": "GSM", "double_skill_access": "AP"},
            {"name": "ChaosChaosWarror", "faction": factions["Chaos Chosen"], "position": "Chaos Warrior", "max_quantity": 4, "price": 100, "movement": 5, "strength": 4, "agility": 3, "armour": 9, "starting_skills": "-", "normal_skill_access": "GSM", "double_skill_access": "AP"},
            {"name": "ChaosMinotaur", "faction": factions["Chaos Chosen"], "position": "Minotaur", "max_quantity": 1, "price": 150, "movement": 5, "strength": 5, "agility": 2, "armour": 8, "starting_skills": "Loner, Frenzy, Horns, Mighty Blow, Thick Skull, Wild Animal", "normal_skill_access": "SM", "double_skill_access": "GAP"},
            # Chaos Dwarf
            {"name": "ChaosDwarfHobgoblin", "faction": factions["Chaos Dwarf"], "position": "Hobgoblin", "max_quantity": 16, "price": 40, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "-", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "ChaosDwarfChaosDwarfBlocker", "faction": factions["Chaos Dwarf"], "position": "Chaos Dwarf Blocker", "max_quantity": 6, "price": 70, "movement": 4, "strength": 3, "agility": 2, "armour": 9, "starting_skills": "Block, Tackle, Thick Skull", "normal_skill_access": "GS", "double_skill_access": "APM"},
            {"name": "ChaosDwarfBullCentaur", "faction": factions["Chaos Dwarf"], "position": "Bull Centaur", "max_quantity": 2, "price": 130, "movement": 6, "strength": 4, "agility": 2, "armour": 9, "starting_skills": "Sprint, Sure Feet, Thick Skull", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "ChaosDwarfMinotaur", "faction": factions["Chaos Dwarf"], "position": "Minotaur", "max_quantity": 1, "price": 150, "movement": 5, "strength": 5, "agility": 2, "armour": 8, "starting_skills": "Loner, Frenzy, Horns, Mighty Blow, Thick SKull, Wild Animal", "normal_skill_access": "S", "double_skill_access": "GAPM"},
            # Chaos Renegades
            {"name": "RenegadeHumanLinemen", "faction": factions["Chaos Renegade"], "position": "Human Lineman", "max_quantity": 12, "price": 50, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "-", "normal_skill_access": "GSMP", "double_skill_access": "A"},
            {"name": "RenegadeDarkElfLineman", "faction": factions["Chaos Renegade"], "position": "Dark Elf Lineman", "max_quantity": 1, "price": 70, "movement": 6, "strength": 3, "agility": 4, "armour": 8, "starting_skills": "Animosity", "normal_skill_access": "GAM", "double_skill_access": "PS"},
            # Dark Elf
            {"name": "DarkElfLineman", "faction": factions["Dark Elf"], "position": "Lineman", "max_quantity": 16, "price": 70, "movement": 6, "strength": 3, "agility": 4, "armour": 8, "starting_skills": "-", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "DarkElfRunner", "faction": factions["Dark Elf"], "position": "Runner", "max_quantity": 2, "price": 80, "movement": 7, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Dump-Off", "normal_skill_access": "GAP", "double_skill_access": "S"},
            {"name": "DarkElfAssassin", "faction": factions["Dark Elf"], "position": "Assassin", "max_quantity": 2, "price": 90, "movement": 6, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Shadowing, Stab", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "DarkElfBlitzer", "faction": factions["Dark Elf"], "position": "Blitzer", "max_quantity": 4, "price": 100, "movement": 7, "strength": 3, "agility": 4, "armour": 8, "starting_skills": "Block", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "DarkElfWitchElf", "faction": factions["Dark Elf"], "position": "Witch Elf", "max_quantity": 2, "price": 110, "movement": 7, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Frenzy, Dodge, Jump Up", "normal_skill_access": "GA", "double_skill_access": "SP"},
            # Dwarf
            {"name": "DwarfBlocker", "faction": factions["Dwarf"], "position": "Blocker", "max_quantity": 16, "price": 70, "movement": 4, "strength": 3, "agility": 2, "armour": 9, "starting_skills": "Block, Tackle, Thick Skull", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "DwarfRunner", "faction": factions["Dwarf"], "position": "Runner", "max_quantity": 2, "price": 80, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Sure Hands, Thick Skull", "normal_skill_access": "GP", "double_skill_access": "AS"},
            {"name": "DwarfBlitzer", "faction": factions["Dwarf"], "position": "Blitzer", "max_quantity": 2, "price": 80, "movement": 5, "strength": 3, "agility": 3, "armour": 9, "starting_skills": "Block, Thick Skull", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "DwarfTrollSlayer", "faction": factions["Dwarf"], "position": "Troll Slayer", "max_quantity": 2, "price": 90, "movement": 5, "strength": 3, "agility": 2, "armour": 8, "starting_skills": "Block, Dauntless, Frenzy, Thick Skull", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "DwarfDeathroller", "faction": factions["Dwarf"], "position": "Deathroller", "max_quantity": 1, "price": 160, "movement": 4, "strength": 7, "agility": 1, "armour": 10, "starting_skills": "Loner, Break Tackle, Dirty Player, Juggernaut, Mighty Blow, No Hands, Secret Weapon, Stand Firm", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Elf
            {"name": "ElfLineman", "faction": factions["Elven Union"], "position": "Lineman", "max_quantity": 16, "price": 60, "movement": 6, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "-", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "ElfThrower", "faction": factions["Elven Union"], "position": "Thrower", "max_quantity": 2, "price": 70, "movement": 6, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Pass", "normal_skill_access": "GAP", "double_skill_access": "S"},
            {"name": "ElfCatcher", "faction": factions["Elven Union"], "position": "Catcher", "max_quantity": 4, "price": 100, "movement": 8, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Catch, Nerves of Steel", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "ElfBlitzer", "faction": factions["Elven Union"], "position": "Blitzer", "max_quantity": 2, "price": 110, "movement": 7, "strength": 3, "agility": 4, "armour": 8, "starting_skills": "Block, Side Step", "normal_skill_access": "GA", "double_skill_access": "SP"},
            # Goblin
            {"name": "GoblinGoblin", "faction": factions["Goblin"], "position": "Goblin", "max_quantity": 16, "price": 40, "movement": 6, "strength": 2, "agility": 3, "armour": 7, "starting_skills": "Dodge, Right Stuff, Stunty", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "GoblinBombardier", "faction": factions["Goblin"], "position": "Bombardier", "max_quantity": 1, "price": 40, "movement": 6, "strength": 2, "agility": 3, "armour": 7, "starting_skills": "Bombardier, Dodge, Secret Weapon, Stunty", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "GoblinLooney", "faction": factions["Goblin"], "position": "Looney", "max_quantity": 1, "price": 40, "movement": 6, "strength": 2, "agility": 3, "armour": 7, "starting_skills": "Chainsaw, Secret Weapon, Stunty", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "GoblinFanatic", "faction": factions["Goblin"], "position": "Fanatic", "max_quantity": 1, "price": 70, "movement": 3, "strength": 7, "agility": 3, "armour": 7, "starting_skills": "Ball & Chain, No Hands, Secret Weapon, Stunty", "normal_skill_access": "S", "double_skill_access": "GAP"},
            {"name": "GoblinPogoer", "faction": factions["Goblin"], "position": "Pogoer", "max_quantity": 1, "price": 70, "movement": 7, "strength": 2, "agility": 3, "armour": 7, "starting_skills": "Dodge, Leap, Stunty, Very Long Legs", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "GoblinTroll", "faction": factions["Goblin"], "position": "Troll", "max_quantity": 2, "price": 110, "movement": 4, "strength": 5, "agility": 1, "armour": 9, "starting_skills": "Loner, Always Hungry, Mighty Blow, Really Stupid, Regeneration, Throw Team-Mate", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Halfling
            {"name": "HalflingHalfling", "faction": factions["Halfling"], "position": "Halfling", "max_quantity": 16, "price": 30, "movement": 5, "strength": 2, "agility": 3, "armour": 6, "starting_skills": "Dodge, Right Stuff, Stunty", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "HalflingTreeman", "faction": factions["Halfling"], "position": "Treeman", "max_quantity": 2, "price": 120, "movement": 2, "strength": 6, "agility": 1, "armour": 10, "starting_skills": "Mighty Blow, Stand Firm, Strong Arm, Take Root, Thick Skull, Throw Team-Mate", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # High Elf
            {"name": "HighElfLineman", "faction": factions["High Elf"], "position": "Lineman", "max_quantity": 16, "price": 70, "movement": 6, "strength": 3, "agility": 4, "armour": 8, "starting_skills": "-", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "HighElfThrower", "faction": factions["High Elf"], "position": "Thrower", "max_quantity": 2, "price": 90, "movement": 6, "strength": 3, "agility": 4, "armour": 8, "starting_skills": "Pass, Safe Throw", "normal_skill_access": "GAP", "double_skill_access": "S"},
            {"name": "HighElfCatcher", "faction": factions["High Elf"], "position": "Catcher", "max_quantity": 4, "price": 90, "movement": 8, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Catch", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "HighElfBlitzer", "faction": factions["High Elf"], "position": "Blitzer", "max_quantity": 2, "price": 100, "movement": 7, "strength": 3, "agility": 4, "armour": 8, "starting_skills": "Block", "normal_skill_access": "GA", "double_skill_access": "SP"},
            # Humans
            {"name": "HumanLineman", "faction": factions["Human"], "position": "Lineman", "max_quantity": 16, "price": 50, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "-", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "HumanCatcher", "faction": factions["Human"], "position": "Catcher", "max_quantity": 4, "price": 70, "movement": 8, "strength": 2, "agility": 3, "armour": 7, "starting_skills": "Catch, Dodge", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "HumanThrower", "faction": factions["Human"], "position": "Thrower", "max_quantity": 2, "price": 70, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Sure Hands, Pass", "normal_skill_access": "GP", "double_skill_access": "AS"},
            {"name": "HumanBlitzer", "faction": factions["Human"], "position": "Blitzer", "max_quantity": 4, "price": 90, "movement": 7, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Block", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "HumanOgre", "faction": factions["Human"], "position": "Ogre", "max_quantity": 1, "price": 140, "movement": 5, "strength": 5, "agility": 2, "armour": 9, "starting_skills": "Loner, Bone-head, Mighty Blow, Thick Skull, Throw Team-Mate", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Khemri
            {"name": "KhemriSkeleton", "faction": factions["Tomb Kings"], "position": "Skeleton", "max_quantity": 16, "price": 40, "movement": 5, "strength": 3, "agility": 2, "armour": 7, "starting_skills": "Regeneration, Thick Skull", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "KhemriThro-Ra", "faction": factions["Tomb Kings"], "position": "Thro-Ra", "max_quantity": 2, "price": 70, "movement": 6, "strength": 3, "agility": 2, "armour": 7, "starting_skills": "Pass, Regeneration, Sure Hands", "normal_skill_access": "GP", "double_skill_access": "AS"},
            {"name": "KhemriBlitz-Ra", "faction": factions["Tomb Kings"], "position": "Blitz-Ra", "max_quantity": 2, "price": 90, "movement": 6, "strength": 3, "agility": 2, "armour": 8, "starting_skills": "Block, Regeneration", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "KhemriTombuardian", "faction": factions["Tomb Kings"], "position": "Tomb Guardian", "max_quantity": 4, "price": 100, "movement": 4, "strength": 5, "agility": 1, "armour": 9, "starting_skills": "Decay, Regeneration", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Lizardman
            {"name": "LizardmanSkink", "faction": factions["Lizardmen"], "position": "Skink", "max_quantity": 16, "price": 60, "movement": 8, "strength": 2, "agility": 3, "armour": 7, "starting_skills": "Dodge, Stunty", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "LizardmanSaurus", "faction": factions["Lizardmen"], "position": "Saurus", "max_quantity": 6, "price": 80, "movement": 6, "strength": 4, "agility": 1, "armour": 9, "starting_skills": "-", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "LizardmanKroxigor", "faction": factions["Lizardmen"], "position": "Kroxigor", "max_quantity": 1, "price": 140, "movement": 6, "strength": 5, "agility": 1, "armour": 9, "starting_skills": "Loner, Bone-head, Mighty Blow, Prehensile Tail, Thick Skull", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Necromantic
            {"name": "NecromanticZombie", "faction": factions["Necromantic Horror"], "position": "Zombie", "max_quantity": 16, "price": 40, "movement": 4, "strength": 3, "agility": 2, "armour": 8, "starting_skills": "Regeneration", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "NecromanticGhoul", "faction": factions["Necromantic Horror"], "position": "Ghoul", "max_quantity": 2, "price": 70, "movement": 7, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Dodge", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "NecromanticWight", "faction": factions["Necromantic Horror"], "position": "Wight", "max_quantity": 2, "price": 90, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Block, Regeneration", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "NecromanticFleshGolem", "faction": factions["Necromantic Horror"], "position": "Flesh Golem", "max_quantity": 2, "price": 110, "movement": 4, "strength": 4, "agility": 2, "armour": 9, "starting_skills": "Regeneration, Stand Firm, Thick Skull", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "NecromanticWerewolf", "faction": factions["Necromantic Horror"], "position": "Werewolf", "max_quantity": 2, "price": 120, "movement": 8, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Claws, Frenzy, Regeneration", "normal_skill_access": "GA", "double_skill_access": "SP"},
            # Norse
            {"name": "NorseLineman", "faction": factions["Norse"], "position": "Lineman", "max_quantity": 16, "price": 50, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Block", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "NorseThrower", "faction": factions["Norse"], "position": "Thrower", "max_quantity": 2, "price": 70, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Block, Pass", "normal_skill_access": "GP", "double_skill_access": "AS"},
            {"name": "NorseCatcher", "faction": factions["Norse"], "position": "Catcher", "max_quantity": 2, "price": 90, "movement": 7, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Block, Dauntless", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "NorseBlitzer", "faction": factions["Norse"], "position": "Blitzer", "max_quantity": 2, "price": 90, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Block, Frenzy, Jump Up", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "NorseWerewolf", "faction": factions["Norse"], "position": "Werewolf", "max_quantity": 2, "price": 110, "movement": 6, "strength": 4, "agility": 2, "armour": 8, "starting_skills": "Frenzy", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "NorseYhetee", "faction": factions["Norse"], "position": "Yhetee", "max_quantity": 1, "price": 140, "movement": 5, "strength": 5, "agility": 1, "armour": 8, "starting_skills": "Loner, Claws, Disturbing Presence, Frenzy, Wild Animal", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Nurgle
            {"name": "NurgleRotter", "faction": factions["Nurgle"], "position": "Rotter", "max_quantity": 16, "price": 40, "movement": 5, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Decay, Nurgle's Rot", "normal_skill_access": "GM", "double_skill_access": "ASP"},
            {"name": "NurglePestigor", "faction": factions["Nurgle"], "position": "Pestigor", "max_quantity": 4, "price": 80, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Horns, Nurgle's Rot, Regeneration", "normal_skill_access": "GM", "double_skill_access": "ASP"},
            {"name": "NurgleNurgleWarrior", "faction": factions["Nurgle"], "position": "Nurgle Warrior", "max_quantity": 4, "price": 110, "movement": 4, "strength": 4, "agility": 2, "armour": 9, "starting_skills": "Disturbing Presence, Foul Appearance, Nurgle's Rot, Regeneration", "normal_skill_access": "GSM", "double_skill_access": "AP"},
            {"name": "NurgleBeastOfNurgle", "faction": factions["Nurgle"], "position": "Beast of Nurgle", "max_quantity": 1, "price": 140, "movement": 4, "strength": 5, "agility": 1, "armour": 9, "starting_skills": "Loner, Disturbing Presence, Foul Appearance, Mighty Blow, Nurgle's Rot, Really Stupid, Regeneration, Tentacles", "normal_skill_access": "S", "double_skill_access": "GAPM"},
            # Ogre
            {"name": "OgreSnotling", "faction": factions["Ogre"], "position": "Snotling", "max_quantity": 16, "price": 20, "movement": 5, "strength": 1, "agility": 3, "armour": 5, "starting_skills": "Dodge, Right Stuff, Side Step, Stunty, Titchy", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "OgreOgre", "faction": factions["Ogre"], "position": "Ogre", "max_quantity": 6, "price": 140, "movement": 5, "strength": 5, "agility": 2, "armour": 9, "starting_skills": "Bone-head, Mighty Blow, Thick Skull, Throw Team-Mate", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Orc
            {"name": "OrcLineman", "faction": factions["Orc"], "position": "Lineman", "max_quantity": 16, "price": 50, "movement": 5, "strength": 3, "agility": 3, "armour": 9, "starting_skills": "-", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "OrcGoblin", "faction": factions["Orc"], "position": "Goblin", "max_quantity": 4, "price": 40, "movement": 6, "strength": 2, "agility": 3, "armour": 7, "starting_skills": "Right Stuff, Dodge, Stunty", "normal_skill_access": "A", "double_skill_access": "GSP"},
            {"name": "OrcThrower", "faction": factions["Orc"], "position": "Thrower", "max_quantity": 2, "price": 70, "movement": 5, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Sure Hands, Pass", "normal_skill_access": "GP", "double_skill_access": "AS"},
            {"name": "OrcBlackOrc", "faction": factions["Orc"], "position": "Black Orc", "max_quantity": 4, "price": 80, "movement": 4, "strength": 4, "agility": 2, "armour": 9, "starting_skills": "-", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "OrcBlitzer", "faction": factions["Orc"], "position": "Blitzer", "max_quantity": 4, "price": 80, "movement": 6, "strength": 3, "agility": 3, "armour": 9, "starting_skills": "Block", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "OrcTroll", "faction": factions["Orc"], "position": "Troll", "max_quantity": 1, "price": 110, "movement": 4, "strength": 5, "agility": 1, "armour": 9, "starting_skills": "Loner, Always Hungry, Mighty Blow, Really Stupid, Regeneration, Throw Team-Mate", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Skaven
            {"name": "SkavenLineman", "faction": factions["Skaven"], "position": "Lineman", "max_quantity": 16, "price": 50, "movement": 7, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "-", "normal_skill_access": "G", "double_skill_access": "ASPM"},
            {"name": "SkavenThrower", "faction": factions["Skaven"], "position": "Thrower", "max_quantity": 2, "price": 70, "movement": 7, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Pass, Sure Hands", "normal_skill_access": "GP", "double_skill_access": "ASM"},
            {"name": "SkavenGutterRunner", "faction": factions["Skaven"], "position": "Gutter Runner", "max_quantity": 4, "price": 80, "movement": 9, "strength": 2, "agility": 4, "armour": 7, "starting_skills": "Dodge", "normal_skill_access": "GA", "double_skill_access": "SPM"},
            {"name": "SkavenBlitzer", "faction": factions["Skaven"], "position": "Blitzer", "max_quantity": 2, "price": 80, "movement": 7, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Block", "normal_skill_access": "GS", "double_skill_access": "APM"},
            {"name": "SkavenRatOgre", "faction": factions["Skaven"], "position": "Rat Ogre", "max_quantity": 1, "price": 150, "movement": 6, "strength": 5, "agility": 2, "armour": 8, "starting_skills": "Loner, Frenzy, Mighty Blow, Prehensile Tail, Wild Animal", "normal_skill_access": "S", "double_skill_access": "GAPM"},
            # Undead
            {"name": "UndeadSkeleton", "faction": factions["Shambling Undead"], "position": "Skeleton", "max_quantity": 16, "price": 40, "movement": 5, "strength": 3, "agility": 2, "armour": 7, "starting_skills": "Regeneration, Thick Skull", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "UndeadZombie", "faction": factions["Shambling Undead"], "position": "Zombie", "max_quantity": 16, "price": 40, "movement": 4, "strength": 3, "agility": 2, "armour": 8, "starting_skills": "Regeneration", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "UndeadGhoul", "faction": factions["Shambling Undead"], "position": "Ghoul", "max_quantity": 4, "price": 70, "movement": 7, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "Dodge", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "UndeadWight", "faction": factions["Shambling Undead"], "position": "Wight", "max_quantity": 2, "price": 90, "movement": 6, "strength": 3, "agility": 3, "armour": 8, "starting_skills": "Block, Regeneration", "normal_skill_access": "GS", "double_skill_access": "AP"},
            {"name": "UndeadMummy", "faction": factions["Shambling Undead"], "position": "Mummy", "max_quantity": 2, "price": 120, "movement": 3, "strength": 5, "agility": 1, "armour": 9, "starting_skills": "Mighty Blow, Regeneration", "normal_skill_access": "S", "double_skill_access": "GAP"},
            # Vampire
            {"name": "VampireThrall", "faction": factions["Vampire"], "position": "Thrall", "max_quantity": 16, "price": 40, "movement": 6, "strength": 3, "agility": 3, "armour": 7, "starting_skills": "-", "normal_skill_access": "G", "double_skill_access": "ASP"},
            {"name": "VampireVampire", "faction": factions["Vampire"], "position": "Vampire", "max_quantity": 6, "price": 110, "movement": 6, "strength": 4, "agility": 4, "armour": 8, "starting_skills": "Blood Lust, Hypnotic Gaze, Regeneration", "normal_skill_access": "GAS", "double_skill_access": "P"},
            # Wood Elf
            {"name": "WoodElfLineman", "faction": factions["Wood Elf"], "position": "Lineman", "max_quantity": 16, "price": 70, "movement": 7, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "-", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "WoodElfCatcher", "faction": factions["Wood Elf"], "position": "Catcher", "max_quantity": 4, "price": 90, "movement": 8, "strength": 2, "agility": 4, "armour": 7, "starting_skills": "Catch, Dodge, Sprint", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "WoodElfThrower", "faction": factions["Wood Elf"], "position": "Thrower", "max_quantity": 2, "price": 90, "movement": 7, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Pass", "normal_skill_access": "GAP", "double_skill_access": "S"},
            {"name": "WoodElfWardancer", "faction": factions["Wood Elf"], "position": "Wardancer", "max_quantity": 2, "price": 120, "movement": 8, "strength": 3, "agility": 4, "armour": 7, "starting_skills": "Block, Dodge, Leap", "normal_skill_access": "GA", "double_skill_access": "SP"},
            {"name": "WoodElfTreeman", "faction": factions["Wood Elf"], "position": "Treeman", "max_quantity": 1, "price": 120, "movement": 2, "strength": 6, "agility": 1, "armour": 10, "starting_skills": "Loner, Mighty Blow, Stand Firm, Strong Arm, Take Root, Thick Skull, Throw Team-Mate", "normal_skill_access": "S", "double_skill_access": "GAP"},
        ]

        # Define the base path for icons
        ICON_BASE_PATH = "league_manager/icons/faction_postional_icons/"

        # Append the icon_path to each entry in player_types
        for pt in player_types:
            faction_name = pt["faction"].faction_name.lower().replace(" ", "-")  # Convert to lowercase, replace spaces
            position_name = pt["position"].lower().replace(" ", "-")  # Convert position to lowercase, replace spaces

            pt["icon_path"] = f"{ICON_BASE_PATH}{faction_name}-{position_name}.png"

        for pt in player_types:
            obj, created = PlayerType.objects.get_or_create(name=pt["name"], faction=pt["faction"], position=pt["position"], max_quantity=pt["max_quantity"], price=pt["price"], movement=pt["movement"], strength=pt["strength"], agility=pt["agility"], armour=pt["armour"], starting_skills=pt["starting_skills"], normal_skill_access=pt["normal_skill_access"], double_skill_access=pt["double_skill_access"], icon_path=pt["icon_path"])
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


