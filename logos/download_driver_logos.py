import os
import requests

logos = {
    "ALB": "https://media.formula1.com/d_driver_images/v1707233023/content/dam/fom-website/drivers/ALEXANDER_ALBON.png",
    "ALO": "https://media.formula1.com/d_driver_images/v1707233047/content/dam/fom-website/drivers/FERNANDO_ALONSO.png",
    "BOT": "https://media.formula1.com/d_driver_images/v1707233069/content/dam/fom-website/drivers/VALTTERI_BOTTAS.png",
    "GAS": "https://media.formula1.com/d_driver_images/v1707233096/content/dam/fom-website/drivers/PIERRE_GASLY.png",
    "HAM": "https://media.formula1.com/d_driver_images/v1707233117/content/dam/fom-website/drivers/LEWIS_HAMILTON.png",
    "HUL": "https://media.formula1.com/d_driver_images/v1707233136/content/dam/fom-website/drivers/NICO_HULKENBERG.png",
    "LEC": "https://media.formula1.com/d_driver_images/v1707233153/content/dam/fom-website/drivers/CHARLES_LECLERC.png",
    "MAG": "https://media.formula1.com/d_driver_images/v1707233172/content/dam/fom-website/drivers/KEVIN_MAGNUSSEN.png",
    "NOR": "https://media.formula1.com/d_driver_images/v1707233191/content/dam/fom-website/drivers/LANDO_NORRIS.png",
    "OCO": "https://media.formula1.com/d_driver_images/v1707233211/content/dam/fom-website/drivers/ESTEBAN_OCON.png",
    "PER": "https://media.formula1.com/d_driver_images/v1707233230/content/dam/fom-website/drivers/SERGIO_PEREZ.png",
    "PIA": "https://media.formula1.com/d_driver_images/v1707233251/content/dam/fom-website/drivers/OSCAR_PIASTRI.png",
    "RIC": "https://media.formula1.com/d_driver_images/v1707233269/content/dam/fom-website/drivers/DANIEL_RICCIARDO.png",
    "RUS": "https://media.formula1.com/d_driver_images/v1707233287/content/dam/fom-website/drivers/GEORGE_RUSSELL.png",
    "SAI": "https://media.formula1.com/d_driver_images/v1707233305/content/dam/fom-website/drivers/CARLOS_SAINZ.png",
    "SAR": "https://media.formula1.com/d_driver_images/v1707233323/content/dam/fom-website/drivers/LOGAN_SARGEANT.png",
    "STR": "https://media.formula1.com/d_driver_images/v1707233340/content/dam/fom-website/drivers/LANCE_STROLL.png",
    "TSU": "https://media.formula1.com/d_driver_images/v1707233358/content/dam/fom-website/drivers/YUKI_TSUNODA.png",
    "VER": "https://media.formula1.com/d_driver_images/v1707233378/content/dam/fom-website/drivers/MAX_VERSTAPPEN.png",
    "ZHO": "https://media.formula1.com/d_driver_images/v1707233397/content/dam/fom-website/drivers/GUANYU_ZHOU.png"
}

os.makedirs("logos", exist_ok=True)

for code, url in logos.items():
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"logos/{code}.png", 'wb') as f:
                f.write(response.content)
            print(f"✅ {code}.png downloaded")
        else:
            print(f"❌ Failed to download {code}")
    except Exception as e:
        print(f"❌ Error with {code}: {e}")
