ISS Tracker
__________________________________________________________________________________________________________________________________________________________________________________

## Inspiration

This project was inspired by Terence Eden's insightful blog post: [Get the location of the ISS using DNS](https://shkspr.mobi/blog/2025/07/get-the-location-of-the-iss-using-dns/).

-----

## What Does This Script Do?

This is a straightforward Python script designed to track the current position of the International Space Station (ISS). It fetches the ISS's real-time coordinates via a **DNS LOC record** and then determines which country or ocean the ISS is currently flying over.

-----

## How It Works

The ISS's position is provided as a DNS LOC record by `where-is-the-iss.dedyn.io`. The script performs the following steps:

1.  **DNS Query**: It makes a DNS query to retrieve the LOC record.
2.  **Coordinate Parsing**: It parses the latitude, longitude, and altitude from the DNS response.
3.  **Location Determination**:
      * It attempts to identify the precise location (country, city, or body of water) using **OpenStreetMap/Nominatim** for reverse geocoding.
      * If Nominatim cannot determine a specific location (e.g., when the ISS is over an ocean), the script will estimate the broader geographical region itself.

-----

## Installation

To get started, follow these steps:

```bash
# Clone the repository
git clone https://github.com/deinusername/iss-tracker.git
cd iss-tracker

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate # For Linux/macOS
# or
venv\Scripts\activate    # For Windows

# Install the required dependencies
pip install dnspython OSMPythonTools
```

-----

## Usage

Simply run the script from your terminal:

```bash
python3 iss_tracker.py
```

### Example Output

```
ISS Tracker
========================================
DNS LOC Record: 43 18 21.050 S 67 33 49.440 E 428960.00m 10000.00m 10000.00m 10000.00m

ISS Position:
  Breite:  -43.3058°
  Länge:   67.5637°
  Höhe:    428.1 km

Location wird bestimmt...
  Über:    Indischer Ozean, Südhemisphäre

========================================
```

-----

## Requirements

  * **Python 3.6+**
  * [`dnspython`](https://www.google.com/search?q=%5Bhttps://pypi.org/project/dnspython/%5D\(https://pypi.org/project/dnspython/\)) for DNS LOC queries.
  * [`OSMPythonTools`](https://www.google.com/search?q=%5Bhttps://pypi.org/project/OSMPythonTools/%5D\(https://pypi.org/project/OSMPythonTools/\)) for reverse geocoding using OpenStreetMap.

-----

## Technical Details

### DNS LOC Records Explained

The ISS position is ingeniously provided as a DNS LOC record. While typically used for static locations (like an office address), this project leverages it for real-time tracking, showcasing a clever application of an existing standard.

### Coordinate Parsing

The LOC record is delivered in a specific format, such as:

```
43 18 21.050 S 67 33 49.440 E 428960.00m ...
```

The script parses these degrees, minutes, and seconds, converting them into standard decimal degrees for latitude and longitude, and extracts the altitude in meters.

### Location Determination Strategy

1.  The primary method uses **OpenStreetMap's Nominatim API** to perform reverse geocoding, identifying specific places or larger geographical features.
2.  If Nominatim doesn't return a result (which is common when the ISS is over vast oceans), the script falls back to calculating the approximate region based solely on the coordinates.

-----

## Limitations

  * **Nominatim API Rate Limits**: The Nominatim API has a rate limit (typically 1 request per second), which can affect performance if you try to make too many requests too quickly.
  * **Oceanic Accuracy**: Location accuracy is limited when the ISS is over oceans, as there are no specific landmasses to identify.
  * **Approximation of Borders**: Country borders are approximate, not pixel-perfect.
  * **Data Dependency**: The script relies on the `where-is-the-iss.dedyn.io` service to keep the DNS record updated.

-----

## Potential Enhancements

  * **Continuous Tracking**: Implement an option for the script to continuously update the ISS position every `X` seconds.
  * **Map Visualization**: Integrate a map (e.g., using a library like Folium or Basemap) to graphically display the ISS's current location.
  * **Overhead Predictions**: Add functionality to predict when the ISS will fly over a specific user-defined location.
  * **Improved Ocean Identification**: Develop more refined methods for identifying specific ocean regions or hemispheres.
  * **Graphical User Interface (GUI)**: Create a user-friendly GUI instead of a command-line interface.

-----

## Why DNS LOC?

Traditional ISS APIs often require API keys or can experience downtime. DNS, in contrast, is nearly always available and incredibly fast, making this a robust and ingenious solution for real-time tracking.

-----

## Troubleshooting

### "Konnte ISS Position nicht abrufen" (Could not retrieve ISS position)

  * Check your internet connection.
  * The DNS server providing the ISS data might be temporarily down.
  * Your firewall might be blocking DNS queries.

### "Konnte Koordinaten nicht parsen" (Could not parse coordinates)

  * The format of the LOC record might have changed. This could happen if the data service updates its output.

### "Location wird bestimmt..." hängt (Location is being determined... hangs)

  * The Nominatim API might be overloaded. Try running the script again after a short wait.

-----

**Fun Fact:** The ISS travels at approximately 28,000 km/h (17,500 mph), completing an orbit around the Earth in just about 90 minutes\!

__________________________________________________________________________________________________________________________________________________________________________________
