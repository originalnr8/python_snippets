from math import sin, cos, tan, sqrt, pi, acos, atan, atan2, isnan
import sys

you = [ "", "", "" ] # latitude, longitude, altitude
them = [ "", "", "" ] # latitude, longitude, altitude
aim = [ 0.0, 0.0, 0.0 ] # distance, azimuth, altitude

debug = True
debug_coords = [ "51.528308", "-0.3817801", "10.0", 
                 "-27.3649395", "152.970454", "15.67" ]

def parseAngle( id, limit ):
    angle = float(id)
    if (isnan(angle) == True or angle < -limit or angle > limit):
        return limit +1
    else:
        return angle

def parseElevation(id):
    angle = float(id)
    if (isnan(angle) == True):
        return -1
    else:
        return angle

def parseLocation(stringarray):
    location = []

    lim = 90.0
    latitude = parseAngle(stringarray[0], lim)
    if latitude > lim:
        return []
        
    lim = 180.0
    longitude = parseAngle(stringarray[1], lim)
    if longitude > 180.0:
        return []

    elevation = parseElevation(stringarray[2])
    if elevation < 0:
        return []
    location = [ latitude, longitude, elevation ]
    return location

def calculateEartRadius(latitudeRadians):
    a = 6378137.0 # equatorial radius
    b = 6356752.3 # polar raidus
    cosLat = cos(latitudeRadians)
    sinLat = sin(latitudeRadians)
    t1 = a * a * cosLat
    t2 = b * b * sinLat
    t3 = a * cosLat
    t4 = b * sinLat
    radius = sqrt((t1*t1 + t2*t2) / (t3*t3 + t4*t4))
    return radius

def calculateGeocentricLatitude(latitude):
    e2 = 0.00669437999014
    clat = atan((1.0 - e2) * tan(latitude))
    return clat

def calculatLocationToPoint(c):
    latitude = c[0] * (pi/180.0)
    longitude = c[1] * (pi/180.0)
    radius = calculateEartRadius(latitude)
    clat = calculateGeocentricLatitude(latitude)
    cosLon = cos(longitude)
    sinLon = sin(longitude)
    cosLat = cos(latitude)
    sinLat = sin(latitude)
    x = radius * cosLon * cosLat
    y = radius * sinLon * cosLat
    z = radius * sinLat
    cosGlat = cos(latitude)
    sinGlat = sin(latitude)
    nx = cosGlat * cosLon
    ny = cosGlat * sinLon
    nz = sinGlat
    x += c[2] * nx
    y += c[2] * ny
    z += c[2] * nz
    return [ x, y, z, radius, nx, ny, nz ]

def calculateDistance(ap, bp):
    dx = ap[0] - bp[0]
    dy = ap[1] - bp[1]
    dz = ap[2] - bp[2]
    return sqrt((dx*dx) + (dy*dy) + (dz*dz))

def rotateGlobe (b, a, bradius, aradius):
        # Get modified coordinates of 'b' by rotating the globe so that 'a' is at lat=0, lon=0.
        br = [ b[0], (b[1] - a[1]), b[2] ]
        brp = calculatLocationToPoint(br)
        # Rotate brp cartesian coordinates around the z-axis by a.lon degrees, then around the y-axis by a.lat degrees.
        # Though we are decreasing by a.lat degrees, as seen above the y-axis, this is a positive (counterclockwise) rotation (if B's longitude is east of A's).
        # However, from this point of view the x-axis is pointing left.
        # So we will look the other way making the x-axis pointing right, the z-axis pointing up, and the rotation treated as negative.
        alat = calculateGeocentricLatitude((a[0] * -1) * (pi / 180.0))
        acos = cos(alat)
        asin = sin(alat)
        bx = (brp[0] * acos) - (brp[2] * asin)
        by = brp[1]
        bz = (brp[0] * asin) + (brp[2] * acos)
        return [ bx, by, bz, bradius ]

def normalizeVectorDiff(b, a):
        # Calculate norm(b-a), where norm divides a vector by its length to produce a unit vector.
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        dz = b[2] - a[2]
        dist2 = (dx*dx) + (dy*dy) + (dz*dz)
        if dist2 == 0:
            return []
        dist = sqrt(dist2)
        return [ (dx/dist), (dy/dist), (dz/dist), 1.0 ]

def Calculate():
    a = parseLocation(you)
    if a != []:
        b = parseLocation(them)
        if b != []:
            ap = calculatLocationToPoint(a)
            bp = calculatLocationToPoint(b)
            distKm = 0.001 * calculateDistance(ap, bp)
            aim[0] = distKm

            # Let's use a trick to calculate azimuth:
            # Rotate the globe so that point A looks like latitude 0, longitude 0.
            # We keep the actual radii calculated based on the oblate geoid, but use angles based on subtraction.
            # Point A will be at x=radius, y=0, z=0.
            # Vector difference B-A will have dz = N/S component, dy = E/W component.
            br = rotateGlobe(b, a, bp[3], ap[3])
            if ((br[2]*br[2]) + (br[1]*br[1]) > 1.0e-6):
                theta = atan2(br[2], br[1]) * (180.0 / pi)
                azimuth = 90.0 - theta
                if azimuth < 0.0:
                    azimuth += 360.0
                if azimuth > 360.0:
                    azimuth -= 360.0
                aim[1] = azimuth
            bma = normalizeVectorDiff(bp, ap)
            if bma != []:
                # Calculate altitude, which is the angle above the horizon of B as seen from A.
                # Almost always, B will actually be below the horizon, so the altitude will be negative.
                # The dot product of bma and norm = cos(zenith_angle), and zenith_angle = (90 deg) - altitude.
                # So altitude = 90 - acos(dotprod).
                altitude = 90.0 - ((180.0 / pi) * acos((bma[0] * ap[4]) + (bma[1] * ap[5]) + (bma[2] * ap[6])))
                aim[2] = altitude
        else:
            print("")
    else:
        print("")
                
def geostationary():
    them[0] = 0 # assume satellite is directly above equator.
    them[2] = 35786000  # 35,786 km above equator.

def checkArguements():
    if debug == True:
        return debug_coords
    arguments = sys.argv[1:]
    if len(arguments) >= 6:
        return arguments
    else:
        print("Arguments to supply are:")
        print("                         Your Latitude")
        print("                         Your Longitude")
        print("                         Your Altiude")
        print("                         Its Latitude")
        print("                         Its Longitude")
        print("                         Its Altitude")
        print("                         [Geostationary] - If you are targeting a geostationary satellite its latitude and altitude will be added with the optional flag")
        return []

def main():
    args = checkArguements()
    for x in range(0,3):
        you[x] = args[x]
    for y in range(0,3):
        them[y] = args[y+3]
    if len(args)> 7:
        geostationary()
    Calculate()
    if debug == True:
        print("Ascension: {0} degrees".format(aim[1]))
        print("Declination: {0} degrees".format(aim[2]))
        print("Distance: {0} km".format(aim[0]))
    else:
        print("{0} {1} {2}".format(aim[0], aim[1], aim[2]))

main()