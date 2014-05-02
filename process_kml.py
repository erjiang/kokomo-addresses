from __future__ import print_function
import re
import xml.etree.ElementTree as ET
import sys

import process_addresses

KML_NS = "{http://earth.google.com/kml/2.2}"

def main(infile):
    kml = ET.parse(infile)
    root = kml.getroot()

    points = root.findall(".//%sPlacemark" % KML_NS)

    osm = process_addresses.newroot()

    for point in points:

        coordinate_tag = point.find('.//%scoordinates' % KML_NS)
        if coordinate_tag is None:
            process_addresses.log("No coordinate found")
            continue

        lon, lat, _ = coordinate_tag.text.split(",")

        name_tag = point.find("%sname" % KML_NS)
        if name_tag is None:
            process_addresses.log("Found point at %s, %s without name" % (lat, lon))
            continue

        name = name_tag.text
        name = re.sub('\\D+$', '', name)  # remove non-numbers

        process_addresses.newnode(osm, lat, lon, { 'addr:housenumber': name })

    osm_doc = ET.ElementTree(osm)
    osm_doc.write(sys.stdout, encoding="UTF-8")


if __name__ == "__main__":
    main(sys.stdin)
