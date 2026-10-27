
import requests
import xml.etree.ElementTree as ET

url = "https://maps.isric.org/mapserv"
params = {
    "map": "/map/silt.map",
    "SERVICE": "WCS",
    "VERSION": "2.0.1",
    "REQUEST": "GetCapabilities",
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

root = ET.fromstring(response.content)
ns = {"wcs": "http://www.opengis.net/wcs/2.0"}

for item in root.findall(".//wcs:CoverageId", ns):
    print(item.text)
