import os
from PIL import Image
import requests
from io import BytesIO

# Mapping of driver stints with teams by year (simplified for example)
driver_team_by_year = {
    'HAM': {
        '2020': 'Mercedes',
        '2021': 'Mercedes',
        '2022': 'Mercedes',
        '2023': 'Mercedes',
        '2024': 'Mercedes',
        '2025': 'Ferrari',
    },
    # Add more drivers if needed
}

# Sample team logos mapping (real URLs should be added)
team_logos = {
    'Mercedes': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9c/Mercedes-Benz_logo_2010.svg/220px-Mercedes-Benz_logo_2010.svg.png',
    'Ferrari': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d4/Scuderia_Ferrari_Logo.svg/220px-Scuderia_Ferrari_Logo.svg.png',
}

def download_logo(driver_code, year, save_dir='logos'):
    year = str(year)
    team = driver_team_by_year.get(driver_code, {}).get(year, None)

    if not team:
        return f"No team data found for {driver_code} in {year}"

    logo_url = team_logos.get(team, None)
    if not logo_url:
        return f"No logo URL found for team {team}"

    response = requests.get(logo_url)
    if response.status_code == 200:
        os.makedirs(save_dir, exist_ok=True)
        img = Image.open(BytesIO(response.content))
        file_path = os.path.join(save_dir, f"{driver_code}_{year}_{team}.png")
        img.save(file_path)
        return f"Logo saved at: {file_path}"
    else:
        return f"Failed to download logo for {team}"

# Example: Download Hamilton's logo based on 2024
download_logo('HAM', 2024)

