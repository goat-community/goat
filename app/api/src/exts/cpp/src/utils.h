#include "types.h"
#include "csv.h"
#include <fstream>
#include <regex>

void replace_all(
    std::string &s,
    std::string const &toReplace,
    std::string const &replaceWith)
{
    std::ostringstream oss;
    std::size_t pos = 0;
    std::size_t prevPos = pos;

    while (true)
    {
        prevPos = pos;
        pos = s.find(toReplace, pos);
        if (pos == std::string::npos)
            break;
        oss << s.substr(prevPos, pos - prevPos);
        oss << replaceWith;
        pos += toReplace.size();
    }

    oss << s.substr(prevPos);
    s = oss.str();
}

std::vector<std::string> split(const std::string &input, const std::string &regex = " ")
{
    std::regex re(regex);
    std::sregex_token_iterator first{input.begin(), input.end(), re, -1}, last; // the '-1' is what makes the regex split (-1 := what was not matched)
    std::vector<std::string> tokens{first, last};
    return tokens;
}

std::vector<Edge>
read_file(std::string name_file)
{
    std::vector<Edge> data_edges;
    Edge edge;
    std::ifstream myfile;
    std::string line;
    myfile.open(name_file, std::ios::in);

    int lineCount = 0;
    std::getline(myfile, line); // ignore header line
    while (std::getline(myfile, line) && !line.empty())
    {
        std::vector<std::string> segmented = split(line, "(\\,\\[\\[)");
        std::vector<std::string> props = split(segmented[0], "(\\,)");
        edge.id = std::stoll(props[0]);
        edge.source = std::stoll(props[1]);
        edge.target = std::stoll(props[2]);
        edge.cost = std::stod(props[3]);
        edge.reverse_cost = std::stod(props[4]);
        edge.length = std::stod(props[5]);
        // Remove last brackets ]] and split geometry coordinate pairs.
        segmented[1].erase(segmented[1].length() - 2);
        std::vector<std::string> coords = split(segmented[1], "(\\]\\,\\[)");

        // Loop through coords
        std::vector<std::array<double, 2>> geometry;
        for (auto coord : coords)
        {
            std::array<double, 2> xy;
            std::vector<std::string> xy_str = split(coord, "(\\,)");
            xy[0] = std::stod(xy_str[0]);
            xy[1] = std::stod(xy_str[1]);
            geometry.push_back(xy);
        }
        edge.geometry = geometry;
        data_edges.push_back(edge);
        lineCount++;
    }

    myfile.close();
    return data_edges;
}

void read_geometry(std::string &geom_string, Edge &edge)
{
    std::array<double, 2> coords;
    replace_all(geom_string, "[", "");
    replace_all(geom_string, "]", "");
    replace_all(geom_string, ",", "");
    std::stringstream ss(geom_string);
    char peek_;
    bool set_x = true;
    for (double i; ss >> i;)
    {
        if (set_x)
        {
            coords[0] = i;
            set_x = false;
        }
        else
        {
            coords[1] = i;
            edge.geometry.push_back(coords);
            set_x = true;
        }
    }
}

int count_lines(std::string file_name)
{
    std::ifstream infile;
    infile.open(file_name);
    int count = std::count(std::istreambuf_iterator<char>(infile),
                           std::istreambuf_iterator<char>(), '\n');
    infile.close();
    return count;
}

Edge *
read_network_csv(std::string name_file, int64_t &total_edges)
{
    io::CSVReader<7, io::trim_chars<' ', '\t', '"'>, io::double_quote_escape<',', '\"'>> in(name_file);
    int64_t line_count = count_lines(name_file);
    Edge edge;
    Edge *data_edges = new Edge[line_count];
    total_edges = line_count - 2;
    std::string coordinates;
    in.read_header(io::ignore_extra_column,
                   "id",
                   "source",
                   "target",
                   "length_3857",
                   "cost",
                   "reverse_cost",
                   "coordinates_3857");

    in.next_line();

    int i = 0;
    while (in.read_row(data_edges[i].id,
                       data_edges[i].source,
                       data_edges[i].target,
                       data_edges[i].length,
                       data_edges[i].cost,
                       data_edges[i].reverse_cost,
                       coordinates))
    {
        read_geometry(coordinates, data_edges[i]);
        i++;
    }
    std::cout << "Read network complete.\n";
    return data_edges;
}