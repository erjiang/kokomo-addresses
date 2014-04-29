from __future__ import print_function
import xml.etree.ElementTree as ET
import sys
"""Script to process Kokomo address data in OSM format, and generate
a cleaned up, porperly tagged OSM file."""

INITIAL_ID = -747


def main(infile):
    osm = ET.parse(infile)
    root = osm.getroot()

    count_no_textstring = 0

    for node in root:
        textstringnode = node.find("tag[@k='TEXTSTRING']")
        if textstringnode is None:
            count_no_textstring += 1
            continue
        textstring = textstringnode.attrib['v']
        log(textstring)

    log("----")
    log("%d nodes without textstring" % count_no_textstring)
    log("%d nodes total" % len(root))


def newnode(root, lat, lon, tags={}):
    "Creates and returns a new <node> element."
    n = ET.Element("node")
    n.attrib['id'] = newid()
    n.attrib['lat'] = lat
    n.attrib['lon'] = lon
    n.attrib['visible'] = True
    root.append(n)

    for k, v in tags:
        n.append(ET.Element("tag", attrib={
            "k": k,
            "v": v
            }))

    return n


def newid():
    "Generates the next (negative) ID number."
    global INITIAL_ID
    INITIAL_ID -= 1
    return INITIAL_ID


def parse_addr(text):
    pass 

def expand_addr(text):
    return text


def log(text):
    if isinstance(text, str):
        sys.stderr.write(text)
    else:
        sys.stderr.write(repr(text))
    sys.stderr.write("\n")


if __name__ == "__main__":
    main(sys.stdin)
