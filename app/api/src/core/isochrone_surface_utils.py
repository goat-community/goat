def line_length(line):
    return pow(
        pow(line["end_point"][1] - line["start_point"][1], 2)
        + pow(line["end_point"][0] - line["start_point"][0], 2),
        0.5,
    )


def compute_distance(start_point, end_point):
    return pow(pow(end_point[1] - start_point[1], 2) + pow(end_point[0] - start_point[0], 2), 0.5)


def slope(line):
    # TODO: when lines are vertical or horizontal
    return (line["end_point"][1] - line["start_point"][1]) / (
        line["end_point"][0] - line["start_point"][0]
    )


def compute_xy_step(line, split_length):
    # TODO: when lines are vertical or horizontal
    xy = {}
    xy["x"] = split_length * (line["end_point"][0] - line["start_point"][0]) / line_length(line)
    if xy["x"] == 0:
        xy["y"] = (
            split_length
            * (line["end_point"][1] - line["start_point"][1])
            / abs(line["end_point"][1] - line["start_point"][1])
        )
    else:
        xy["y"] = xy["x"] * slope(line)
    return xy


def get_next_point(current_point, xy):
    next_point = []
    next_point[0] = current_point[0] + xy["x"]
    next_point[1] = current_point[1] + xy["y"]

    return next_point


def get_previous_point(current_point, xy):
    previous_point = []
    previous_point[0] = current_point[0] - xy["x"]
    previous_point[1] = current_point[1] - xy["y"]
    return previous_point


def resize_boundry(boundry, point):

    if point[0] > boundry["max_x"]:
        boundry["max_x"] = point[0]

    if point[0] < boundry["min_x"]:
        boundry["min_x"] = point[0]

    if point[1] > boundry["max_y"]:
        boundry["max_y"] = point[1]

    if point[1] < boundry["min_y"]:
        boundry["min_y"] = point[1]

    return boundry, point


def point_reached_line(line, point):
    if line["end_point"][0] > line["start_point"][0]:
        return point[0] >= line["end_point"][0] or point[0] <= line["start_point"][0]

    elif line["end_point"][0] < line["start_point"][0]:
        return point[0] <= line["end_point"][0] or point[0] >= line["start_point"][0]

    elif line["end_point"][1] > line["start_point"][1]:
        return point[1] >= line["end_point"][1] or point[1] <= line["start_point"][1]

    elif line["end_point"][1] < line["start_point"][1]:
        return point[1] <= line["end_point"][1] or point[1] >= line["start_point"][1]

    return True  # TODO: Why?


def compute_cost(split_length, network_edge):
    network_cost = network_edge["end_cost"] - network_edge["start_cost"]
    return split_length * network_cost / network_edge["length"]


def compute_cost(
    split_length, network_edge_end_cost, network_edge_start_cost, network_edge_length
):

    network_edge_cost = network_edge_end_cost - network_edge_start_cost
    return split_length * network_edge_cost / network_edge_length


def split_line(
    line,
    split_length,
    network_edge_end_cost,
    network_edge_start_cost,
    network_edge_length,
    split_cost,
    boundry,
    cost_result,
):

    xy_step = compute_xy_step(line, split_length)
    next_cost = network_edge_start_cost
    # start point of line shouldn't be added so skip.
    next_point = line.start_point
    next_point = get_next_point(line, next_point, xy_step)
    next_cost = next_cost + split_cost
    while not point_reached_line(line, next_point):
        cost_result["points"].append(next_point)
        cost_result["costs"].append(next_cost)

        resize_boundry(boundry, next_point)

        next_point = get_next_point(line, next_point, xy_step)
        next_cost = next_cost + split_cost

    previous_point = get_previous_point(line, next_point, xy_step)
    previous_cost = next_cost - split_cost
    distance_last_point_to_line_end = compute_distance(line["end_point"], previous_point)
    next_cost = previous_cost + compute_cost(
        distance_last_point_to_line_end,
        network_edge_end_cost,
        network_edge_start_cost,
        network_edge_length,
    )
    cost_result["points"].append(line["end_point"])
    cost_result["costs"].append(next_cost)

    resize_boundry(boundry, line["end_point"])
