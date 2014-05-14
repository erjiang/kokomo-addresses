from __future__ import print_function

import math
import re
import xml.etree.ElementTree as ET
import sys

import process_addresses

SPLITS = 0.02

def main(infile):
    osm = ET.parse(infile)
    root = osm.getroot()

    chunks = {}

    def truncate(n):
        return math.floor(n / SPLITS)

    for node in root:
        lat = float(node.attrib['lat'])
        lon = float(node.attrib['lon'])
        chunk_id = (truncate(lat), truncate(lon))
        if chunk_id not in chunks:
            chunks[chunk_id] = process_addresses.newroot()


        chunks[chunk_id].append(node)

    process_addresses.log("%d chunks" % len(chunks))
    process_addresses.log("Writing files...")

    for chunk_id, root in chunks.iteritems():
        doc = ET.ElementTree(root)
        name = "chunks_%f-%f.osm" % chunk_id
        process_addresses.log(name)
        with open(name, 'w') as f:
            doc.write(f, encoding="UTF-8")


if __name__ == "__main__":
    main(sys.stdin)
