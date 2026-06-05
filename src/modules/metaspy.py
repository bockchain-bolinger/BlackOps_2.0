"""
metaspy.py - Image Forensics & GPS Extractor
"""

import argparse
import json
import os
import sys

from colorama import Fore, init
from exif import Image

from src.core.base_module import BaseModule

init(autoreset=True)


class MetaSpy(BaseModule):
    name = "MetaSpy"

    def banner(self):
        self.clear()
        print(f"""{Fore.MAGENTA}
    __  ___      __        _____            
   /  |/  /___  / /_____ / ___/____  __  __
  / /|_/ / _ \\/ __/ __ \\\\__ \\/ __ \\/ / / /
 / /  / /  __/ /_/ /_/ /__/ / /_/ / /_/ / 
/_/  /_/\\___/\\__/\\__,_/____/ .___/\\__, /  
                          /_/    /____/   
{Fore.WHITE}   >> IMAGE FORENSICS & GPS EXTRACTOR <<
""")

    def decimal_coords(self, coords, ref) -> float:
        decimal = coords[0] + coords[1] / 60 + coords[2] / 3600
        return -decimal if ref in ("S", "W") else decimal

    def analyze_image(self, image_path: str) -> dict | None:
        image_path = image_path.strip().strip("'\"")
        print(f"{Fore.WHITE}[*] Analysiere: {Fore.YELLOW}{image_path}")

        if not os.path.exists(image_path):
            print(f"{Fore.RED}[ERROR] Datei nicht gefunden.")
            return None

        try:
            with open(image_path, "rb") as f:
                img = Image(f)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Konnte nicht lesen: {e}")
            return None

        if not img.has_exif:
            print(f"{Fore.RED}[-] Keine EXIF-Daten vorhanden.")
            return None

        result = {}

        print(f"\n{Fore.CYAN}[EXIF] Basis-Informationen:")
        for attr, label in [
            ("make", "Hersteller"),
            ("model", "Modell"),
            ("datetime_original", "Aufnahmedatum"),
            ("software", "Software"),
            ("image_width", "Breite"),
            ("image_length", "Hoehe"),
        ]:
            try:
                val = getattr(img, attr)
                print(f"  {label:15s}: {val}")
                result[attr] = str(val)
            except AttributeError:
                pass

        print(f"\n{Fore.CYAN}[GPS] Koordinaten:")
        try:
            lat = self.decimal_coords(img.gps_latitude, img.gps_latitude_ref)
            lon = self.decimal_coords(img.gps_longitude, img.gps_longitude_ref)
            print(f"  {Fore.GREEN}Breitengrad:  {lat:.6f}")
            print(f"  {Fore.GREEN}Laengengrad:  {lon:.6f}")
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            print(f"\n{Fore.YELLOW}  [MAPS] {maps_url}")
            result["gps"] = {"lat": lat, "lon": lon, "maps": maps_url}
        except AttributeError:
            print(f"  {Fore.RED}[-] Keine GPS-Koordinaten vorhanden.")

        return result

    def run(self):
        self.banner()
        path = input(f"{Fore.GREEN}[?] Bildpfad: ").strip()
        result = self.analyze_image(path)

        if result and self.confirm("Ergebnisse als JSON exportieren?"):
            fname = f"metaspy_{os.path.basename(path)}.json"
            try:
                with open(fname, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"{Fore.GREEN}[OK] {fname}")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] {e}")

        self.pause()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MetaSpy - Image Forensics")
    parser.add_argument("image", nargs="?", help="Pfad zum Bild")
    parser.add_argument("--version", action="version", version="MetaSpy v3.0")

    if len(sys.argv) == 1:
        MetaSpy().run()
    else:
        args = parser.parse_args()
        tool = MetaSpy()
        tool.banner()
        tool.analyze_image(args.image)
