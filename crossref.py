from __future__ import print_function

from collections import defaultdict
from process_addresses import log
import xml.etree.ElementTree as ET
import process_addresses
import geo
import sys

"""This program takes one OSM file that contains points with addr:housenumber
and addr:street and cross-references all points with a second file containing
points with addr:housenumber. If two housenumbers in both files are close
enough, it will take the number and street name from the first file, and use
the location from the second file."""

# distance that two points have to be in order to be considered the same addr
NEAR_THRESHOLD = 34  # meters

def main(f1, f2, of_good, of_bad):
    # using housenumber and street from first file
    addrf1 = ET.parse(f1)
    root1 = addrf1.getroot()

    # checking against and using lat/lon from second file
    addrf2 = ET.parse(f2)
    root2 = addrf2.getroot()

    newroot = process_addresses.newroot()

    # docroot to store bad address nodes
    badroot = process_addresses.newroot()

    numberlocs = defaultdict(list)  # Map str [(float, float)]

    for node in root2:
        housenumbertag = node.find("tag[@k='addr:housenumber']")
        housenumber = housenumbertag.attrib['v']
        lat = float(node.attrib['lat'])
        lon = float(node.attrib['lon'])
        numberlocs[housenumber].append((lat, lon))
    log("%d house numbers indexed" % len(root2))

    for node in root1:
        lat = float(node.attrib['lat'])
        lon = float(node.attrib['lon'])
        housenumbertag = node.find("tag[@k='addr:housenumber']")
        housenumber = housenumbertag.attrib['v']

        # skip anything that doesn't also exist in addrf2
        if not numberlocs[housenumber]:
            log("No results found for number [%s]" % housenumber)
            badroot.append(node)
            continue

        f2_ref, f2_ref_dist = find_closest_node((lat, lon), numberlocs[housenumber])
        if not f2_ref or f2_ref_dist > NEAR_THRESHOLD:
            log("Results for number [%s] too far" % housenumber)
            badroot.append(node)
            continue

        streettag = node.find("tag[@k='addr:street']")
        street = streettag.attrib['v']
        if street is None:
            log("Broke on house number %s" % housenumber)

        newlat, newlon = f2_ref
        process_addresses.newnode(newroot, str(newlat), str(newlon), {
            "addr:housenumber": housenumber,
            "addr:street": street
            })
    log("%d total addresses processed" % len(root1))
    log("%d addresses successfully cross-referenced" % len(newroot))

    newdoc = ET.ElementTree(newroot)
    newdoc.write(open(of_good, 'w'), encoding="UTF-8")

    if of_bad:
        baddoc = ET.ElementTree(badroot)
        baddoc.write(open(of_bad, 'w'), encoding="UTF-8")
        
def find_closest_node(ref, coords):
    """Given ref=(lat, lon) and coords=[(lat, lon), ...], find the closest coord."""


    closest = None
    closest_dist = 100000 # arbitrary high number
    for coord in coords:
        dist = geo.haversine(ref, coord)
        if dist < closest_dist:
            closest = coord
            closest_dist = dist
    return closest, closest_dist


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.stderr.write("Usage: conflate.py numbers_streets.osm numbers_locs.osm outfile.osm bad_addresses.osm")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
