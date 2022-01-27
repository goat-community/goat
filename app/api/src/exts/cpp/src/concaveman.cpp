/*
<%
setup_pybind11(cfg)
%>
*/

//
// Author: Stanislaw Adaszewski, 2019
//

// BSD 2-Clause License

// Copyright (c) 2019, sadaszewski
// All rights reserved.

// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.

// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include "concaveman.h"

#ifndef DEBUG
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
#endif

#ifndef DEBUG
py::array_t<double> ccm(
    py::array_t<double> points_,
    py::array_t<int32_t> hull_points_,
    double concavity, double lengthThreshold)
{

    auto points_c = points_.unchecked<2>();
    auto num_points = points_c.shape(0);
    if (points_c.shape(1) != 2)
    {
        throw std::invalid_argument("points must be 2d");
    }

    auto hull_points_c = hull_points_.unchecked<1>();
    auto num_hull_points = hull_points_c.shape(0);

    typedef double T;
    typedef std::array<T, 2> point_type;

    std::vector<point_type> points(num_points);
    for (auto i = 0; i < num_points; i++)
    {
        points[i] = {points_c(i, 0), points_c(i, 1)};
    }

    std::vector<int32_t> hull(num_hull_points);
    for (auto i = 0; i < num_hull_points; i++)
    {
        hull[i] = hull_points_c(i);
    }

    auto concave_points = concaveman<T, 16>(points, hull, concavity, lengthThreshold);

    py::array_t<double> result({concave_points.size(), size_t(2)});
    auto result_ptr = result.mutable_unchecked<2>();

    for (size_t i = 0; i < concave_points.size(); i++)
    {
        result_ptr(i, 0) = concave_points[i][0];
        result_ptr(i, 1) = concave_points[i][1];
    }

    return result;
}

PYBIND11_MODULE(concaveman, m)
{
    m.def("concaveman", &ccm);
}
#endif