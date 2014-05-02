from __future__ import print_function

import re
import xml.etree.ElementTree as ET
import sys

import expansions

"""Script to process Kokomo address data in OSM format, and generate
a cleaned up, porperly tagged OSM file."""

INITIAL_ID = -747


def main(infile):
    osm = ET.parse(infile)
    root = osm.getroot()

    count_no_textstring = 0

    # tree for storing good nodes
    processed_root = newroot()

    # tree for storing nodes that have problems (unparseable addrs)
    problems_root = newroot()

    for node in root:
        textstringnode = node.find("tag[@k='TEXTSTRING']")
        if textstringnode is None:
            count_no_textstring += 1
            continue
        textstring = textstringnode.attrib['v']
        parsed = parse_addr(textstring)
        if not parsed:
            newnode(problems_root, node.attrib['lat'], node.attrib['lon'],
                    { "TEXTSTRING": textstring })
        else:
            housenumber, street = parsed
            newnode(processed_root, node.attrib['lat'], node.attrib['lon'], {
                "addr:housenumber": housenumber,
                "addr:street": street
                })
            log('%s\t\t%s' % parsed)

    log("----")
    log("%d nodes without textstring" % count_no_textstring)
    log("%d nodes total" % len(root))

    processed_doc = ET.ElementTree(processed_root)
    processed_doc.write(sys.stdout, encoding="UTF-8")


def newroot():
    root = ET.Element("osm")
    root.attrib['version'] = '0.6'
    root.attrib['upload'] = 'true'
    root.attrib['generator'] = 'erjiang/kokomo-addresses'
    return root


def newnode(root, lat, lon, tags={}):
    "Creates and returns a new <node> element."
    n = ET.Element("node")
    n.attrib['id'] = newid()
    n.attrib['lat'] = lat
    n.attrib['lon'] = lon
    n.attrib['visible'] = "true"
    root.append(n)

    for k, v in tags.iteritems():
        n.append(ET.Element("tag", attrib={
            "k": k,
            "v": v
            }))

    return n


def newid():
    "Generates the next (negative) ID number."
    global INITIAL_ID
    INITIAL_ID -= 1
    return str(INITIAL_ID)


def parse_addr(text):
    matches = re.match('(\\d+)\\s+(.+)', text)
    if not matches:
        return None

    housenumber = matches.group(1)
    street = expand_street(matches.group(2))

    return (housenumber, street)


def expand_street(text):
    # expand directions
    def expand_dir(abbr_match):
        abbr = abbr_match.group()
        if abbr in expansions.directions:
            return expansions.directions[abbr]
        else:
            return abbr
    text = re.sub("\\b[NSEW]{,2}\\b", expand_dir, text)

    # expand road type
    def expand_road(abbr_match):
        abbr = abbr_match.group()
        if abbr in expansions.road_types:
            return expansions.road_types[abbr]
        else:
            return abbr
    text = re.sub('\\b\\w{,5}$', expand_road, text)
    return text


def log(text):
    if isinstance(text, str):
        sys.stderr.write(text)
    else:
        sys.stderr.write(repr(text))
    sys.stderr.write("\n")


if __name__ == "__main__":
    main(sys.stdin)
