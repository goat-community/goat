#include "../src/types.h"
#include "../src/isochrone-surface.h"

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
    return 0;
}