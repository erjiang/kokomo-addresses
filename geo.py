import math

"""Utilities file copied from DoubleMap source code. Need just haversine
distance for now."""

def haversine(origin, destination):
    """Takes two (lat, lon) tuples and returns the distance between them
    in meters."""
    lat1, lon1 = origin
    lat2, lon2 = destination

    # check for invalid values
    if lat1 > 90 or lat1 < -90 or lat2 > 90 or lat2 < -90:
        raise ValueError("Invalid latitude (should be between +/- 90)")
    if lon1 > 180 or lon1 < -180 or lon2 > 180 or lon2 < -180:
        raise ValueError("Invalid longitude (should be between +/- 180)")

    radius = 6378100 # radius of Earth in meters

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d
