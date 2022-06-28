"""
Translated from https://github.com/goat-community/goat/blob/0089611acacbebf4e2978c404171ebbae75591e2/app/client/src/utils/Jsolines.js
"""

import math

import numpy as np
from shapely.geometry import Point, Polygon

MAX_COORDS = 20000


def get_contour(surface, width, height, cutoff):
    """
    Get a contouring grid. Exported for testing purposes, not generally used
    outside jsolines testing
    """
    contour = np.zeros((width - 1) * (height - 1), dtype=np.int8)

    # compute contour values for each cell
    for x in range(width - 1):
        for y in range(height - 1):
            index = y * width + x
            topLeft = surface[index] < cutoff
            topRight = surface[index + 1] < cutoff
            botLeft = surface[index + width] < cutoff
            botRight = surface[index + width + 1] < cutoff

            # if we're at the edge of the area, set the outer sides to false, so that
            # isochrones always close even when they actually extend beyond the edges
            # of the surface

            if x == 0:
                topLeft = botLeft = False
            if x == width - 2:
                topRight = botRight = False
            if y == 0:
                topLeft = topRight = False
            if y == height - 2:
                botRight = botLeft = False

            idx = 0

            if topLeft:
                idx |= 1 << 3
            if topRight:
                idx |= 1 << 2
            if botRight:
                idx |= 1 << 1
            if botLeft:
                idx |= 1

            contour[y * (width - 1) + x] = idx

    return contour


def followLoop(idx, xy, prev_xy):
    """
    Follow the loop
    We keep track of which contour cell we're in, and we always keep the filled
    area to our left. Thus we always indicate only which direction we exit the
    cell.
    """
    x = xy[0]
    y = xy[1]
    prevx = prev_xy[0]
    prevy = prev_xy[1]

    if idx in (1, 3, 7):
        return [x - 1, y]
    elif idx in (2, 6, 14):
        return [x, y + 1]
    elif idx in (4, 12, 13):
        return [x + 1, y]
    elif idx == 5:
        # Assume that saddle has // orientation (as opposed to \\). It doesn't
        # really matter if we're wrong, we'll just have two disjoint pieces
        # where we should have one, or vice versa.
        # From Bottom:
        if prevy > y:
            return [x + 1, y]

        # From Top:
        if prevy < y:
            return [x - 1, y]

        return [x, y]
    elif idx in (8, 9, 11):
        return [x, y - 1]
    elif idx == 10:
        # From left
        if prevx < x:
            return [x, y + 1]

        # From right
        if prevx > x:
            return [x, y - 1]

        return [x, y]

    else:
        return [x, y]


def interpolate(pos, cutoff, start, surface, width, height):
    """
    Do linear interpolation
    """
    #   The edges are always considered unreachable to avoid edge effects so set
    #   them to the cutoff.
    x = pos[0]
    y = pos[1]
    startx = start[0]
    starty = start[1]
    index = y * width + x
    topLeft = surface[index]
    topRight = surface[index + 1]
    botLeft = surface[index + width]
    botRight = surface[index + width + 1]
    if x == 0:
        topLeft = botLeft = cutoff
    if y == 0:
        topLeft = topRight = cutoff
    if y == height - 2:
        botRight = botLeft = cutoff
    if x == width - 2:
        topRight = botRight = cutoff
    # From left
    if startx < x:
        frac = (cutoff - topLeft) / (botLeft - topLeft)
        return [x, y + ensureFractionIsNumber(frac, "left")]
    # From right
    if startx > x:
        frac = (cutoff - topRight) / (botRight - topRight)
        return [x + 1, y + ensureFractionIsNumber(frac, "right")]
    # From bottom
    if starty > y:
        frac = (cutoff - botLeft) / (botRight - botLeft)
        return [x + ensureFractionIsNumber(frac, "bottom"), y + 1]
    # From top
    if starty < y:
        frac = (cutoff - topLeft) / (topRight - topLeft)
        return [x + ensureFractionIsNumber(frac, "top"), y]
    pass


def noInterpolate(pos, start):
    x = pos[0]
    y = pos[1]
    startx = start[0]
    starty = start[1]
    # From left
    if startx < x:
        return [x, y + 0.5]
    # From right
    if startx > x:
        return [x + 1, y + 0.5]
    # From bottom
    if starty > y:
        return [x + 0.5, y + 1]
    # From top
    if starty < y:
        return [x + 0.5, y]
    pass


def logError(object):
    pass


# Calculated fractions may not be numbers causing interpolation to fail.
def ensureFractionIsNumber(frac, direction):
    if math.isnan(frac) or math.isinf(frac):
        logError(
            f"Segment fraction from ${direction} is ${frac}; if this is at the edge of the query this is expected."
        )
        return 0.5
    return frac


def jsolines(
    cutoff,
    height,
    project,
    surface,
    width,
    maxCoordinates=MAX_COORDS,
    interpolation=True,
):
    contour = get_contour(surface, width, height, cutoff)
    cWidth = width - 1

    # Store warnings
    warnings = []

    # JavaScript does not have boolean arrays.
    found = np.zeros((width - 1) * (height - 1), dtype=np.int8)

    # DEBUG, comment out to save memory
    indices = []

    # We'll sort out what shell goes with what hole in a bit.
    shells = []
    holes = []

    # Find a cell that has a line in it, then follow that line, keeping filled
    # area to your left. This lets us use winding direction to determine holes.

    for origx in range(height - 1):
        for origy in range(width - 1):
            index = origy * cWidth + origx
            if found[index] == 1:
                continue
            idx = contour[index]

            # Continue if there is no line here or if it's a saddle, as we don't know which way the saddle goes.
            if idx == 0 or idx == 5 or idx == 10 or idx == 15:
                continue

            # Huzzah! We have found a line, now follow it, keeping the filled area to our left,
            # which allows us to use the winding direction to determine what should be a shell and
            # what should be a hole
            pos = [origx, origy]
            prev = [-1, -1]
            start = [-1, -1]

            # Track winding direction
            direction = 0
            coords = []

            # Make sure we're not traveling in circles.
            # NB using index from _previous_ cell, we have not yet set an index for this cell

            while found[index] != 1:
                prev = start
                start = pos
                idx = contour[index]

                indices.append(idx)

                # Mark as found if it's not a saddle because we expect to reach saddles twice.
                if idx != 5 and idx != 10:
                    found[index] = 1

                if idx == 0 or idx >= 15:
                    warnings.append("Ran off outside of ring")
                    break

                # Follow the loop
                pos = followLoop(idx, pos, prev)
                index = pos[1] * cWidth + pos[0]

                # Keep track of winding direction
                direction += (pos[0] - start[0]) * (pos[1] + start[1])

                # Shift exact coordinates
                if interpolation:
                    coord = interpolate(pos, cutoff, start, surface, width, height)
                else:
                    coord = noInterpolate(pos, start)

                if not coord:
                    warnings.append(
                        f"Unexpected coordinate shift from ${start[0]}, ${start[1]} to ${pos[0]}, ${pos[1]}, discarding ring"
                    )
                    break

                coords.append(project(coord))

                # TODO Remove completely? May be unnecessary.
                if len(coords) > maxCoordinates:
                    warnings.append(f"Ring coordinates > ${maxCoordinates} found, skipping")
                    break

                # We're back at the start of the ring
                if pos[0] == origx and pos[1] == origy:
                    coords.append(coords[0])  # close the ring

                    # make it a fully-fledged GeoJSON object
                    geom = {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": [coords]},
                    }

                    # Check winding direction. Positive here means counter clockwise,
                    # see http:#stackoverflow.com/questions/1165647
                    # +y is down so the signs are reversed from what would be expected
                    if direction > 0:
                        shells.append(geom)
                    else:
                        holes.append(geom)
                    break

        if found[index] == 1:
            warnings.append(
                [
                    f"Ring crosses other ring (or possibly self) at ${pos[0]}, ${pos[1]} coming from case ${idx}",
                    f"Last few indices: ${indices[max(0, len(indices) - 10)].join(',')}",
                ]
            )

    # Shell game time. Sort out shells and holes.
    for hole in holes:

        # Only accept holes that are at least 2-dimensional.
        vertices = [f"{x-y}" for x, y in hole.geometry.coordinates[0]]
        # vertices = Object.keys(
        #   hole.geometry.coordinates[0].reduce((unique, [lat, lng]) => {
        #     unique[`${lat}-${lng}`] = null;
        #     return unique;
        #   }, {})
        # );

        if len(vertices) >= 3:
            # NB this is checking whether the first coordinate of the hole is inside
            # the shell. This is sufficient as shells don't overlap, and holes are
            # guaranteed to be completely contained by a single shell.
            holePoint = Point(hole.geometry.coordinates[0][0])
            containingShell = filter(lambda shell: Polygon(shell).contains(holePoint), shells)

            if containingShell:
                containingShell.geometry.coordinates.append(hole.geometry.coordinates[0])
            else:
                logError("Did not find fitting shell for hole")
