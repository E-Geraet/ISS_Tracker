import dns.resolver
import re
import time
import os
from OSMPythonTools.nominatim import Nominatim


class WorldMap:
    """ASCII Weltkarte für ISS-Anzeige - basierend auf SR Linux Satellite Tracker"""
    
    def __init__(self):
        self.worldmap_list = [

               "   |                                                                       |",
            "   |                                                                       |",
            "   |          . _..::__:  ,-\"-\"._        |]       ,     _,.__              |",
            "   |  _.___ _ _<_>`!(._`.`-.    /         _._     `_ ,_/  '  '-._.---.-.__ |",
            "   |.{     \" \"  -==,',._\\{  \\  /  {) _   / _ \">_,-' `                 /-/_ |",
            "   |\\.:--.        ._ )`^-.  \\\"'     / ( [_/(                        __,/-' |",
            "   |'\"'    \\        \"    _\\         -_,--'                        /. (|    |",
            "   |       |           ,'          _)_.\\\\._ <> {}             _,' /  '     |",
            "   |       `.         /           [_/_'   \"(                <'}  )         |",
            "   |        \\\\    .-. )           /   `-'\\\"...' `:._          _)  '        |",
            "   |          \\  (   `(          /         `:\\  > \\  ,-^.  /' '            |",
            "   |           `._,   \"\"         |           \\`'   \\|   ?_)  {\\            |",
            "   |               =.---.        `._._       ,'     \"`  |' ,- '.           |",
            "   |                |    `-._         |     /          `:`<_|=--._         |",
            "   |                (        >        .     | ,          `=.__.`-'\\        |",
            "   |                  .     /         |     |{|               ,-.,\\        |",
            "   |                  |   ,'           \\   / `'             ,\"     `\\      |",
            "   |                  |  /              |_'                 |  __   /      |",
            "   |                  | |                                   '-'  `-'     \\.|",
            "   |                  |/                                          \"      / |",
            "   |                  \\.                                                '  |",
            "   |                                                                       |",
            "   |                   ,/           _ _____._.--._ _..---.---------.       |",
            "   |__,-----\"-..?----_/ )\\    . ,-'\"              \"                  (__--/|",
            "   |                    /__/\\/                                             |",
            "   |                                                                       |"
        ]
        
        self.width = 71  
        self.height = len(self.worldmap_list)
    
    def _map_coordinates(self, x, in_min, in_max, out_min, out_max):
        """Koordinaten von einem Bereich in einen anderen umrechnen"""
        return round((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    
    def display_iss(self, lat, lon, location_info=None):
        """ISS auf der Weltkarte anzeigen - Format vom SR Linux Plugin adaptiert"""
        
        worldmap = [list(line) for line in self.worldmap_list]
        
       
        map_lat = self._map_coordinates(float(lat), 90, -90, 0, self.height - 1)
        map_lon = self._map_coordinates(float(lon), -180, 180, 1, self.width)  # +1 wegen Pipe
        
       
        if 0 <= map_lat < self.height and 1 <= map_lon < self.width:
            worldmap[map_lat][map_lon] = '\033[5;31m#\033[0m'
        
        
        position = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
        data = [
            f"\tName        : International Space Station",
            f"\tID          : 25544 (NORAD)",
            f"\tTimestamp   : {time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"\tLatitude    : {lat:.6f}°",
            f"\tLongitude   : {lon:.6f}°",
            f"\tLocation    : {location_info or 'Unknown'}",
            f"\tAltitude    : ~408 km (typical ISS orbit)",
            f"\tVelocity    : ~27,600 km/h",
            f"\tOrbital Per.: ~92 minutes",
            f"\tVisibility  : Variable",
            f"\tData Source : DNS LOC Record",
            f"\tResolver    : where-is-the-iss.dedyn.io",
            f"\tCharacter   : \033[92m'#'\033[00m (blinking red)",
            f"\tNext Update : {time.strftime('%H:%M:%S', time.localtime(time.time() + 10))}"
        ]
        
        
        print("\n" + "=" * 100)
        print("ISS LIVE TRACKER - DNS LOC Record Method".center(100))
        print("=" * 100)
        
        for i, row in enumerate(worldmap):
            if i in position and position.index(i) < len(data):
                line = "".join(row) + data[position.index(i)]
            else:
                line = "".join(row)
            print(line)
        
        print("=" * 100)


def get_iss_dns_location():
    """Holt die ISS Position über DNS LOC Record"""
    try:
        result = dns.resolver.resolve('where-is-the-iss.dedyn.io', 'LOC')
        if result:
            return result[0].to_text()
    except dns.resolver.NXDOMAIN:
        print("Fehler: DNS Domain existiert nicht")
    except dns.resolver.Timeout:
        print("Fehler: DNS Timeout")
    except dns.resolver.NoAnswer:
        print("Fehler: Keine Antwort vom DNS")
    except Exception as e:
        print(f"DNS Fehler: {e}")
    return None


def parse_loc_record(loc_str):
    """Parsed den LOC Record String und extrahiert Lat/Lon/Alt"""
    pattern = r"(\d{1,2})\s+(\d{1,2})\s+(\d{1,2}(?:\.\d+)?)\s+([NS])\s+(\d{1,3})\s+(\d{1,2})\s+(\d{1,2}(?:\.\d+)?)\s+([EW])\s+(-?\d+(?:\.\d+)?)m"
    
    match = re.search(pattern, loc_str)
    if not match:
        print(f"Konnte LOC Record nicht parsen: {loc_str}")
        return None

    lat_d, lat_m, lat_s, lat_dir = match.groups()[0:4]
    lon_d, lon_m, lon_s, lon_dir = match.groups()[4:8]
    altitude = match.group(9)

    try:
        # In Dezimalgrad umrechnen
        lat_decimal = float(lat_d) + float(lat_m)/60 + float(lat_s)/3600
        lon_decimal = float(lon_d) + float(lon_m)/60 + float(lon_s)/3600
        
        # Vorzeichen setzen
        if lat_dir == 'S':
            lat_decimal = -lat_decimal
        if lon_dir == 'W':
            lon_decimal = -lon_decimal
            
        return lat_decimal, lon_decimal, float(altitude)
    except ValueError:
        print("Fehler beim Konvertieren der Koordinaten")
        return None


def get_location_info(lat, lon):
    """Bestimmt den Standort - erweitert um Ozean-Erkennung vom SR Linux Code"""
    location = try_nominatim(lat, lon)
    if location:
        return location
    
    return guess_location_from_coords(lat, lon)


def try_nominatim(lat, lon):
    """Nominatim Reverse Geocoding mit verschiedenen Zoom-Levels"""
    nominatim = Nominatim()
    
    for zoom in [10, 8, 6, 4, 3]:
        try:
            result = nominatim.query(lat, lon, reverse=True, zoom=zoom)
            if not result:
                continue
                
            data = result.toJSON()
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                
                if isinstance(first, dict) and 'error' in first:
                    continue
                
                name = first.get('display_name', '')
                address = first.get('address', {})
                
                # Land zuerst probieren
                if address and 'country' in address:
                    return address['country']
                
                # Ozean info
                if address and ('ocean' in address or 'sea' in address):
                    ocean = address.get('ocean') or address.get('sea')
                    return ocean
                
                # Display name als fallback
                if name:
                    ocean_words = ['ocean', 'sea', 'atlantic', 'pacific', 'indian', 'arctic']
                    if any(word in name.lower() for word in ocean_words):
                        return name
                    
                    if ',' in name:  # Wahrscheinlich ein sinnvoller Ort
                        return name
                    
            time.sleep(1)  # Rate limiting
            
        except Exception:
            continue
    
    return None


def guess_location_from_coords(lat, lon):
    """Erweiterte Location-Bestimmung basierend auf SR Linux Satellite Tracker Logik"""
   
    countries = [
        (25, 71, -168, -52, "North America"), 
        (14, 33, -118, -86, "Mexico/Central America"),
        (36, 71, -10, 40, "Europe"),
        (35, 80, 26, 180, "Asia"),
        (-55, 13, -82, -34, "South America"),
        (-35, 37, -18, 52, "Africa"),
        (-47, -10, 113, 154, "Australia/Oceania"),
        (60, 85, -180, 180, "Arctic Region"),
        (-90, -60, -180, 180, "Antarctic Region"),
    ]
    
    for min_lat, max_lat, min_lon, max_lon, name in countries:
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return name
    
   
    ocean = determine_ocean(lat, lon)
    hemisphere = "Northern" if lat > 0 else "Southern"
    
    return f"{ocean}, {hemisphere} Hemisphere"


def determine_ocean(lat, lon):
    """Erweiterte Ozean-Bestimmung"""
    # Spezielle Regionen zuerst
    if lat > 66:
        return "Arctic Ocean"
    elif lat < -60:
        return "Southern Ocean"
    
    # Hauptozeane
    if (lon >= 120 and lon <= 180) or (lon >= -180 and lon <= -70):
        return "Pacific Ocean"
    elif -70 <= lon < 20:
        return "Atlantic Ocean" 
    elif 20 <= lon < 120:
        return "Indian Ocean"
    
    return "Unknown Ocean"


def live_tracking(interval=10):
    """Live-Tracking der ISS - vereinfachte Version des SR Linux Agents"""
    world_map = WorldMap()
    
    print("ISS Live-Tracker gestartet (DNS LOC Method)")
    print("Drücke Ctrl+C zum Beenden")
    print("Basiert auf SR Linux Satellite Tracker von Nokia")
    print("=" * 60)
    
    try:
        while True:
            # Screen clearen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # ISS Position holen
            loc_data = get_iss_dns_location()
            if not loc_data:
                print("Konnte ISS Position nicht abrufen")
                time.sleep(interval)
                continue
            
            # Koordinaten parsen
            coords = parse_loc_record(loc_data)
            if not coords:
                print("Konnte Koordinaten nicht parsen")
                time.sleep(interval)
                continue
            
            lat, lon, alt = coords
            
            # Location bestimmen
            location = get_location_info(lat, lon)
            
            # Weltkarte mit ISS anzeigen
            world_map.display_iss(lat, lon, location)
            
            print(f"\nHöhe: {alt/1000:.1f} km (aus DNS LOC Record)")
            print(f"Nächstes Update in {interval} Sekunden...")
            print(f"DNS LOC Record: {loc_data}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nISS-Tracker beendet!")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'live':
        # Live-Modus
        interval = 10
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                print("Ungültiges Intervall, verwende 10 Sekunden")
        
        live_tracking(interval)
    else:
        
        print("ISS Tracker - DNS LOC Record Method")
        print("Basiert auf Nokia SR Linux Satellite Tracker")
        print("=" * 50)
        
        
        loc_data = get_iss_dns_location()
        if not loc_data:
            print("Konnte ISS Position nicht abrufen")
            exit(1)
        
        print(f"DNS LOC Record: {loc_data}")
        
        
        coords = parse_loc_record(loc_data)
        if not coords:
            print("Konnte Koordinaten nicht parsen")
            exit(1)
        
        lat, lon, alt = coords
        
        
        location = get_location_info(lat, lon)
        
        
        world_map = WorldMap()
        world_map.display_iss(lat, lon, location)
        
        print(f"\nHöhe: {alt/1000:.1f} km")
        print("\nFür Live-Tracking: python iss_tracker.py live [intervall_sekunden]")
        print("=" * 50)
