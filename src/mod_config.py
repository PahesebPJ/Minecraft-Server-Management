import json
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModEntry:
    """Represents a single mod to be downloaded."""
    platform: str  # 'modrinth' or 'curseforge'
    slug: str      # Mod slug/identifier
    version: str   # Version constraint (e.g., 'latest', specific version)
    
    def __post_init__(self):
        """Validate mod entry fields."""
        if self.platform not in ['modrinth', 'curseforge']:
            raise ValueError(f"Invalid platform: {self.platform}. Must be 'modrinth' or 'curseforge'")
        if not self.slug:
            raise ValueError("Mod slug cannot be empty")


@dataclass
class ModConfig:
    """Represents the complete mod configuration."""
    mod_loader: str           # 'forge' or 'fabric'
    minecraft_version: str    # Minecraft version (e.g., '1.21.1')
    mods: List[ModEntry]      # List of mods to download
    
    def __post_init__(self):
        """Validate configuration fields."""
        if self.mod_loader not in ['forge', 'fabric']:
            raise ValueError(f"Invalid mod loader: {self.mod_loader}. Must be 'forge' or 'fabric'")
        if not self.minecraft_version:
            raise ValueError("Minecraft version cannot be empty")


def load_mod_config(config_path: str) -> Optional[ModConfig]:
    """
    Load and parse a mod configuration file.
    
    Args:
        config_path: Path to the JSON configuration file
    
    Returns:
        ModConfig object or None if loading failed
    """
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        return None
    
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        return validate_mod_config(data)
    
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in configuration file: {e}")
        return None
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None


def validate_mod_config(config_data: dict) -> Optional[ModConfig]:
    """
    Validate and convert configuration data to ModConfig object.
    
    Args:
        config_data: Dictionary containing configuration data
    
    Returns:
        ModConfig object or None if validation failed
    """
    try:
        # Check required fields
        if 'mod_loader' not in config_data:
            print("Missing required field: 'mod_loader'")
            return None
        
        if 'minecraft_version' not in config_data:
            print("Missing required field: 'minecraft_version'")
            return None
        
        if 'mods' not in config_data:
            print("Missing required field: 'mods'")
            return None
        
        # Parse mod entries
        mod_entries = []
        for idx, mod_data in enumerate(config_data['mods']):
            if not isinstance(mod_data, dict):
                print(f"Invalid mod entry at index {idx}: must be an object")
                return None
            
            if 'platform' not in mod_data:
                print(f"Mod at index {idx} missing 'platform' field")
                return None
            
            if 'slug' not in mod_data:
                print(f"Mod at index {idx} missing 'slug' field")
                return None
            
            # Version is optional, default to 'latest'
            version = mod_data.get('version', 'latest')
            
            try:
                mod_entry = ModEntry(
                    platform=mod_data['platform'],
                    slug=mod_data['slug'],
                    version=version
                )
                mod_entries.append(mod_entry)
            except ValueError as e:
                print(f"Invalid mod entry at index {idx}: {e}")
                return None
        
        # Create ModConfig
        try:
            config = ModConfig(
                mod_loader=config_data['mod_loader'],
                minecraft_version=config_data['minecraft_version'],
                mods=mod_entries
            )
            return config
        except ValueError as e:
            print(f"Invalid configuration: {e}")
            return None
    
    except Exception as e:
        print(f"Error validating configuration: {e}")
        return None


def create_example_config(output_path: str, mod_loader: str = "fabric", minecraft_version: str = "1.21.1"):
    """
    Create an example mod configuration file.
    
    Args:
        output_path: Path where to save the example config
        mod_loader: Mod loader type ('forge' or 'fabric')
        minecraft_version: Minecraft version
    """
    example_mods = []
    
    if mod_loader == "fabric":
        example_mods = [
            {
                "platform": "modrinth",
                "slug": "fabric-api",
                "version": "latest"
            },
            {
                "platform": "modrinth",
                "slug": "sodium",
                "version": "latest"
            }
        ]
    else:  # forge
        example_mods = [
            {
                "platform": "modrinth",
                "slug": "jei",
                "version": "latest"
            }
        ]
    
    example_config = {
        "mod_loader": mod_loader,
        "minecraft_version": minecraft_version,
        "mods": example_mods
    }
    
    with open(output_path, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print(f"Example configuration created: {output_path}")
