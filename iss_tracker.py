import dns.resolver
import re
import time
from OSMPythonTools.nominatim import Nominatim


def get_iss_dns_location():
    """
    Holt die ISS Position über DNS LOC Record
    """
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
    """
    Parsed den LOC Record String und extrahiert Lat/Lon/Alt
    """
    # Regex für: "43 18 21.050 S 67 33 49.440 E 428960.00m ..."
    pattern = r"(\d{1,2})\s+(\d{1,2})\s+(\d{1,2}(?:\.\d+)?)\s+([NS])\s+(\d{1,3})\s+(\d{1,2})\s+(\d{1,2}(?:\.\d+)?)\s+([EW])\s+(-?\d+(?:\.\d+)?)m"
    
    match = re.search(pattern, loc_str)
    if not match:
        print(f"Konnte LOC Record nicht parsen: {loc_str}")
        return None

    # Koordinaten extrahieren
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
    """
    Versucht den Standort zu bestimmen - erst über Nominatim, dann über Koordinaten
    """
    # Erst mal Nominatim probieren
    location = try_nominatim(lat, lon)
    if location:
        return location
    
    # Falls das nicht klappt, selbst bestimmen
    return guess_location_from_coords(lat, lon)


def try_nominatim(lat, lon):
    """
    Probiert verschiedene Zoom-Level mit Nominatim
    """
    nominatim = Nominatim()
    
    # Verschiedene Zoom-Level durchprobieren
    for zoom in [10, 8, 6, 4, 3]:
        try:
            result = nominatim.query(lat, lon, reverse=True, zoom=zoom)
            if not result:
                continue
                
            # JSON auslesen
            data = result.toJSON()
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                
                # Fehler abfangen
                if isinstance(first, dict) and 'error' in first:
                    continue
                
                # Nützliche Infos extrahieren
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
    """
    Rät die Location basierend auf den Koordinaten
    """
    # Erst schauen ob es ein bekanntes Land sein könnte
    country = check_country_bounds(lat, lon)
    if country:
        return country
    
    # Sonst ist es wahrscheinlich Ozean
    ocean = figure_out_ocean(lat, lon)
    hemisphere = "Nord" if lat > 0 else "Süd"
    
    return f"{ocean}, {hemisphere}hemisphäre"


def check_country_bounds(lat, lon):
    """
    Schaut ob die Koordinaten in einem bekannten Land liegen
    """
    # Grobe Ländergrenzen - nicht super genau aber ok für ISS
    countries = [
        (25, 50, -125, -66, "USA"),
        (42, 83, -141, -52, "Kanada"), 
        (8, 38, -118, -86, "Mexiko"),
        (36, 72, -9, 40, "Europa"),
        (35, 54, 26, 180, "Asien"),
        (5, 35, 68, 97, "Indien"),
        (18, 54, 73, 135, "China"),
        (45, 78, 19, 180, "Russland"),
        (-55, -10, -74, -34, "Südamerika"),
        (-37, 38, -18, 52, "Afrika"),
        (-47, -10, 113, 154, "Australien"),
    ]
    
    for min_lat, max_lat, min_lon, max_lon, name in countries:
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return name
    
    return None


def figure_out_ocean(lat, lon):
    """
    Bestimmt welcher Ozean es ist
    """
    # Pazifik ist der größte - beide Seiten
    if (lon >= 120 and lon <= 180) or (lon >= -180 and lon <= -70):
        return "Pazifik"
    
    # Atlantik
    elif -70 <= lon < 20:
        return "Atlantik"
    
    # Indischer Ozean
    elif 20 <= lon < 120:
        if lat < -60:
            return "Südlicher Ozean"
        return "Indischer Ozean"
    
    # Arktis
    elif lat > 66:
        return "Arktis"
    
    # Antarktis
    elif lat < -60:
        return "Antarktis"
    
    return "Unbekannter Ozean"


if __name__ == '__main__':
    print("ISS Tracker")
    print("=" * 40)
    
    # ISS Position holen
    loc_data = get_iss_dns_location()
    if not loc_data:
        print("Konnte ISS Position nicht abrufen :(")
        exit(1)
    
    print(f"DNS LOC Record: {loc_data}")
    
    # Koordinaten parsen
    coords = parse_loc_record(loc_data)
    if not coords:
        print("Konnte Koordinaten nicht parsen")
        exit(1)
    
    lat, lon, alt = coords
    
    # Ausgabe
    print(f"\nISS Position:")
    print(f"  Breite:  {lat:.4f}°")
    print(f"  Länge:   {lon:.4f}°")
    print(f"  Höhe:    {alt/1000:.1f} km")
    
    # Location bestimmen
    print(f"\nLocation wird bestimmt...")
    location = get_location_info(lat, lon)
    print(f"  Über:    {location}")
    
    print("\n" + "=" * 40)
