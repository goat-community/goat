#include "types.h"
#include "isochrone2.h"

double line_length(Line line)
{
    return pow(pow(line.end_point[1] - line.start_point[1], 2) + pow(line.end_point[0] - line.start_point[0], 2), .5);
}

double compute_distance(std::array<double, 2> start_point, std::array<double, 2> end_point)
{
    return pow(pow(end_point[1] - start_point[1], 2) + pow(end_point[0] - start_point[0], 2), .5);
}

double slope(Line line)
{
    // TODO: when lines are vertical or horizontal
    return (line.end_point[1] - line.start_point[1]) / (line.end_point[0] - line.start_point[0]);
}

XY compute_xy_step(Line line, double split_length)
{
    // TODO: when lines are vertical or horizontal
    XY xy;
    xy.x = split_length * (line.end_point[0] - line.start_point[0]) / line_length(line);
    xy.y = xy.x * slope(line);
    return xy;
}

std::array<double, 2> get_next_point(Line line, std::array<double, 2> current_point, XY xy)
{
    std::array<double, 2> next_point;
    next_point[0] = current_point[0] + xy.x;
    next_point[1] = current_point[1] + xy.y;
    return next_point;
}

std::array<double, 2> get_previous_point(Line line, std::array<double, 2> current_point, XY xy)
{
    std::array<double, 2> previous_point;
    previous_point[0] = current_point[0] - xy.x;
    previous_point[1] = current_point[1] - xy.y;
    return previous_point;
}

bool point_reached_line(Line line, std::array<double, 2> point)
{
    if (line.end_point[0] > line.start_point[0])
    {
        return point[0] > line.end_point[0] ||
               point[0] < line.start_point[0];
    }
    else if (line.end_point[0] < line.start_point[0])
    {
        return point[0] < line.end_point[0] ||
               point[0] > line.start_point[0];
    }
    else if (line.end_point[1] > line.start_point[1])
    {
        return point[1] > line.end_point[1] ||
               point[1] < line.start_point[1];
    }
    else if (line.end_point[1] < line.start_point[1])
    {
        return point[1] < line.end_point[1] ||
               point[1] > line.start_point[1];
    }
    return true; // TODO: Why?
}

double compute_cost(double split_length, IsochroneNetworkEdge2 network_edge)
{
    auto network_cost = network_edge.end_cost - network_edge.start_cost;
    return split_length * network_cost / network_edge.length;
}

double compute_cost(double split_length,
                    double network_end_cost,
                    double network_start_cost,
                    double network_length)
{
    double network_cost = network_end_cost - network_start_cost;
    return split_length * network_cost / network_length;
}

CostResult split_line(Line line, double split_length,
                      double network_end_cost,
                      double network_start_cost,
                      double network_length,
                      double split_cost)
{
    CostResult cost_result;
    auto network_cost = network_end_cost - network_start_cost;
    auto line_xy = compute_xy_step(line, split_length);
    auto next_cost = network_start_cost;
    // start point of line shouldn't be added so skip.
    auto next_point = line.start_point;
    next_point = get_next_point(line, next_point, line_xy);
    next_cost = next_cost + split_cost;
    while (!point_reached_line(line, next_point))
    {
        cost_result.points.push_back(next_point);
        cost_result.costs.push_back(next_cost);
        next_point = get_next_point(line, next_point, line_xy);
        next_cost = next_cost + split_cost;
    }
    auto previous_point = get_previous_point(line, next_point, line_xy);
    auto previous_cost = next_cost - split_cost;
    auto distance_last_point_to_line_end = compute_distance(line.end_point, previous_point);
    next_cost = previous_cost + compute_cost(distance_last_point_to_line_end,
                                             network_end_cost,
                                             network_start_cost,
                                             network_length);
    // next_point is line.end_point
    cost_result.points.push_back(line.end_point);
    cost_result.costs.push_back(next_cost);

    return cost_result;
}

CostResult split_edges(std::vector<IsochroneNetworkEdge2> network_edges, double split_length)
{
    Line line;

    CostResult cost_result;
    std::array<double, 2> previous_point;
    std::array<double, 2> next_point;
    XY line_xy;
    double next_cost;
    double previous_cost;
    double split_cost;
    int line_pointer;
    double distance_last_point_to_line_end;
    for (auto network_edge : network_edges)
    {
        split_cost = compute_cost(split_length, network_edge);
        next_cost = network_edge.start_cost;
        // Add start_point and it's cost
        cost_result.points.push_back(network_edge.geometry[0]);
        cost_result.costs.push_back(next_cost);

        // loop over edge points
        for (line_pointer = 0; line_pointer < network_edge.geometry.size() - 1; line_pointer++)
        {
            // create_line
            line.start_point = network_edge.geometry[line_pointer];

            line.end_point = network_edge.geometry[line_pointer + 1];
            auto line_result = split_line(line, split_length,
                                          network_edge.end_cost,
                                          network_edge.start_cost,
                                          network_edge.length,
                                          split_cost);

            // TODO: copy results at the end of cost_result or pass &cost_result as parameter
        }
        // Add end_point and it's cost
        // Won't add the edge end point. it will be added in the previous addition.
        // cost_result.points.push_back(network_edge.geometry[line_pointer + 1]);
        // cost_result.costs.push_back(network_edge.end_cost);
    }
    return cost_result;
}