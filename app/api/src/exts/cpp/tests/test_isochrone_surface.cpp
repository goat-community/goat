#include "../src/types.h"
#include "../src/isochrone-surface.h"
#include "../src/utils.h"

#define IS_TRUE(x)                                                                    \
    {                                                                                 \
        if (!(x))                                                                     \
            std::cout << __FUNCTION__ << " failed on line " << __LINE__ << std::endl; \
        else                                                                          \
            std::cout << __FUNCTION__ << " passed\n";                                 \
    }

template <typename T>
bool approx(T input1, T input2)
{
    if (input1 == input2)
        return true;
    if (abs(input1 - input2) * 1.0 / abs(input1 + input2) < 0.001)
        return true;
    return false;
}

void test_line_length()
{
    Line line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = 3;
    line.end_point[1] = 4;
    double answer = 5;
    IS_TRUE(approx(line_length(line), answer));
}

void test_compute_distance()
{
    std::array<double, 2>
        point1 = {0, 0},
        point2 = {3, 4};
    double answer = 5;
    IS_TRUE(approx(compute_distance(point1, point2), answer));
}

void test_slope()
{
    Line line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = 3;
    line.end_point[1] = 4;
    double answer = 4.0 / 3;
    IS_TRUE(approx(slope(line), answer));
}

void test_compute_xy_step()
{
    Line line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = 30;
    line.end_point[1] = 40;
    double split_length = 5;
    XY answer;
    answer.x = 3;
    answer.y = 4;
    IS_TRUE(approx(compute_xy_step(line, split_length).x, answer.x) && approx(compute_xy_step(line, split_length).y, answer.y));

    // Test for minus values;

    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = -30;
    line.end_point[1] = 40;
    split_length = 5;

    answer.x = -3;
    answer.y = 4;
    IS_TRUE(approx(compute_xy_step(line, split_length).x, answer.x) && approx(compute_xy_step(line, split_length).y, answer.y));

    // Test for two minus values;

    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = -30;
    line.end_point[1] = -40;
    split_length = 5;

    answer.x = -3;
    answer.y = -4;
    IS_TRUE(approx(compute_xy_step(line, split_length).x, answer.x) && approx(compute_xy_step(line, split_length).y, answer.y));
}

void test_get_next_point()
{
    Line line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = 30;
    line.end_point[1] = 40;
    double split_length = 5;
    XY xy;
    xy.x = 3;
    xy.y = 4;
    std::array<double, 2> current_point = {6, 8};
    std::array<double, 2> answer = {9, 12};
    IS_TRUE(approx(get_next_point(line, current_point, xy)[0], answer[0]) && approx(get_next_point(line, current_point, xy)[0], answer[0]));

    line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = -30;
    line.end_point[1] = 40;
    split_length = 5;
    xy.x = -3;
    xy.y = 4;
    current_point = {-6, 8};
    answer = {-9, 12};
    IS_TRUE(approx(get_next_point(line, current_point, xy)[0], answer[0]) && approx(get_next_point(line, current_point, xy)[0], answer[0]));
}

void test_get_previous_point()
{
    Line line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = 30;
    line.end_point[1] = 40;
    double split_length = 5;
    XY xy;
    xy.x = 3;
    xy.y = 4;
    std::array<double, 2> current_point = {9, 12};
    std::array<double, 2> answer = {6, 8};
    IS_TRUE(approx(get_previous_point(line, current_point, xy)[0], answer[0]) && approx(get_previous_point(line, current_point, xy)[0], answer[0]));

    line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = -30;
    line.end_point[1] = 40;
    split_length = 5;
    xy.x = -3;
    xy.y = 4;
    current_point = {-9, 12};
    answer = {-6, 8};
    IS_TRUE(approx(get_previous_point(line, current_point, xy)[0], answer[0]) && approx(get_previous_point(line, current_point, xy)[0], answer[0]));
}

void test_point_reached_line()
{
    Line line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = 30;
    line.end_point[1] = 40;
    std::array<double, 2> point = {9, 12};
    IS_TRUE(point_reached_line(line, point) == false);

    line;
    line.start_point[0] = 0;
    line.start_point[1] = 0;
    line.end_point[0] = 30;
    line.end_point[1] = 40;
    point = {31, 41};
    IS_TRUE(point_reached_line(line, point) == true);

    line;
    line.start_point[0] = 30;
    line.start_point[1] = 40;
    line.end_point[0] = 0;
    line.end_point[1] = 0;
    point = {31, 41};
    IS_TRUE(point_reached_line(line, point) == true);

    line;
    line.start_point[0] = 30;
    line.start_point[1] = 40;
    line.end_point[0] = 0;
    line.end_point[1] = 0;
    point = {30, 40};
    IS_TRUE(point_reached_line(line, point) == false);
    std::cout << "But it reached the end of line \n";
}

void test_compute_cost()
{
    IsochroneNetworkEdge2 network_edge;
    network_edge.end_cost = 100;
    network_edge.start_cost = 10;
    network_edge.length = 90;
    double split_length = 2;
    double answer = 2;
    IS_TRUE(approx(compute_cost(split_length, network_edge), answer));
}

void test_split_line()
{
    CostResult cost_result;
    Line line;
    line.start_point = {0, 0};
    line.end_point = {30, 40};
    double split_length = 1;
    double network_end_cost = 200;
    double network_start_cost = 0;
    double network_length = 200;
    double split_cost = 1;
    split_line(line, split_length,
               network_end_cost,
               network_start_cost,
               network_length,
               split_cost,
               cost_result);

    for (int i = 0; i < cost_result.costs.size(); i++)
    {
        std::cout << cost_result.points[i][0] << "\t"
                  << cost_result.points[i][1] << "\t| Cost:"
                  << cost_result.costs[i] << "\n";
    }
}

void test_split_network()
{
    std::string network_file = "../data/network_munich_3600seconds_big.csv";
    Edge *data_edges;
    int64_t total_edges;
    data_edges = read_network_csv(network_file, total_edges);
    std::cout << "Total edges: " << total_edges << "\n";
    std::vector<double> distance_limits = {600};
    std::vector<int64_t> start_vertices{2147483647};
    bool only_minimum_cover = false;
    auto results = compute_isochrone2(data_edges, total_edges, start_vertices,
                                      distance_limits, only_minimum_cover);

    auto results2 = split_edges(results.network, 20);
    std::cout << "Total points: " << results2.points.size() << "\n";
    std::cout << "Isochrone Network: " << results.network.size() << "\n";
}

int main()
{
    test_line_length();
    test_compute_distance();
    test_slope();
    test_compute_xy_step();
    test_get_next_point();
    test_get_previous_point();
    test_point_reached_line();
    test_compute_cost();
    test_split_line();
    test_split_network();
    // auto a = read_csv("network_munich_3600seconds_big.csv");
    // test_split_network();
    return 0;
}