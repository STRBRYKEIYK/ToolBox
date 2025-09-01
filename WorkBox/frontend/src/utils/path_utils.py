"""
Path Utilities Module

This module provides utility functions for handling file paths in a platform-independent way.
"""

import os
from pathlib import Path


def get_assets_path(screen_folder):
    """
    Get the assets path for a specific screen folder.
    
    Args:
        screen_folder (str): The name of the screen folder (e.g., 'emp_screens')
        
    Returns:
        Path: The path to the assets directory
    """
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    # Go up to the src directory and then navigate to the assets
    frontend_dir = current_dir.parent
    assets_path = frontend_dir / "screens" / screen_folder / "assets"
    return assets_path


def get_relative_asset_path(screen_folder, asset_subfolder, filename):
    """
    Get the path to an asset file relative to a screen.
    
    Args:
        screen_folder (str): The name of the screen folder (e.g., 'emp_screens')
        asset_subfolder (str): The subfolder within assets (e.g., 'login_assets')
        filename (str): The filename of the asset
        
    Returns:
        Path: The path to the asset file
    """
    assets_path = get_assets_path(screen_folder)
    return assets_path / asset_subfolder / filename
