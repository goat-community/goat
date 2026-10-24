cmake_minimum_required(VERSION 3.18)
project(routing LANGUAGES CXX)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# --- DuckDB (pre-built release binary, C API only) ---
# MUST match the Python `duckdb` pin in goatlib/pyproject.toml — the routing
# module and the Python process share one address space, so two different
# libduckdb versions collide (symbol/ABI clash → memory corruption, crashes).
#
# The module talks to DuckDB through the stable C API (duckdb.h) only, wrapped
# in src/data/duck.h. DuckDB 2.0 ships no C++ headers, and DuckDB's bundled fmt
# would clash with nigiri's.
set(DUCKDB_VERSION "v2.0.0")

# Detect platform for pre-built binary
if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64|ARM64")
    set(DUCKDB_PLATFORM "linux-arm64")
else()
    set(DUCKDB_PLATFORM "linux-amd64")
endif()

# DuckDB 2.0 renamed the release archive (libduckdb-<platform>.zip before).
string(REGEX REPLACE "^v" "" DUCKDB_VERSION_NUMBER "${DUCKDB_VERSION}")
if(DUCKDB_VERSION_NUMBER VERSION_LESS "2.0.0")
    set(DUCKDB_ARCHIVE "libduckdb-${DUCKDB_PLATFORM}.zip")
else()
    set(DUCKDB_ARCHIVE "duckdb-shared-libs-${DUCKDB_PLATFORM}.tar.gz")
endif()

FetchContent_Declare(
    duckdb
    URL https://github.com/duckdb/duckdb/releases/download/${DUCKDB_VERSION}/${DUCKDB_ARCHIVE}
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(duckdb)

# Expose the C headers only, so nothing can pick up the C++ ones by accident.
set(DUCKDB_INCLUDE_DIR "${CMAKE_BINARY_DIR}/duckdb_include")
file(COPY "${duckdb_SOURCE_DIR}/duckdb.h" DESTINATION "${DUCKDB_INCLUDE_DIR}")
if(EXISTS "${duckdb_SOURCE_DIR}/duckdb_v2.h")
    file(COPY "${duckdb_SOURCE_DIR}/duckdb_v2.h" DESTINATION "${DUCKDB_INCLUDE_DIR}")
endif()

add_library(duckdb SHARED IMPORTED GLOBAL)
set_target_properties(duckdb PROPERTIES
    IMPORTED_LOCATION "${duckdb_SOURCE_DIR}/libduckdb.so"
    INTERFACE_INCLUDE_DIRECTORIES "${DUCKDB_INCLUDE_DIR}"
)
# Install libduckdb.so alongside our module so it can be found at runtime
install(FILES "${duckdb_SOURCE_DIR}/libduckdb.so" DESTINATION routing)

# --- nigiri (C++ transit routing library, pre-built SDK from GitHub releases) ---
if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64|ARM64")
    set(NIGIRI_PLATFORM "arm64")
else()
    set(NIGIRI_PLATFORM "amd64")
endif()

FetchContent_Declare(
    nigiri_sdk
    URL https://github.com/plan4better/nigiri/releases/download/latest-cpp/nigiri-sdk-linux-${NIGIRI_PLATFORM}.tar.gz
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(nigiri_sdk)

set(NIGIRI_SDK_DIR "${nigiri_sdk_SOURCE_DIR}")

if(NOT EXISTS "${NIGIRI_SDK_DIR}/lib/libnigiri.a")
    message(FATAL_ERROR "nigiri SDK missing libnigiri.a at ${NIGIRI_SDK_DIR}/lib/")
endif()

add_library(nigiri STATIC IMPORTED GLOBAL)
set_target_properties(nigiri PROPERTIES
    IMPORTED_LOCATION "${NIGIRI_SDK_DIR}/lib/libnigiri.a"
    INTERFACE_INCLUDE_DIRECTORIES "${NIGIRI_SDK_DIR}/include"
    INTERFACE_LINK_LIBRARIES
        "${NIGIRI_SDK_DIR}/lib/libgtfsrt.a;\
${NIGIRI_SDK_DIR}/lib/libfmt.a;\
${NIGIRI_SDK_DIR}/lib/libgeo.a;\
${NIGIRI_SDK_DIR}/lib/libutl.a;\
${NIGIRI_SDK_DIR}/lib/libdate-tz.a;\
${NIGIRI_SDK_DIR}/lib/libianatzdb.a;\
${NIGIRI_SDK_DIR}/lib/libminiz.a;\
${NIGIRI_SDK_DIR}/lib/liboh.a;\
${NIGIRI_SDK_DIR}/lib/libpugixml.a;\
${NIGIRI_SDK_DIR}/lib/libboost-json.a;\
${NIGIRI_SDK_DIR}/lib/libboost-iostreams.a;\
${NIGIRI_SDK_DIR}/lib/libluajit.a;\
${NIGIRI_SDK_DIR}/lib/libproj.a;\
${NIGIRI_SDK_DIR}/lib/libprotobuf.a;\
${NIGIRI_SDK_DIR}/lib/libutf8_validity.a;\
${NIGIRI_SDK_DIR}/lib/libz.a;\
${NIGIRI_SDK_DIR}/lib/libsqlite3.a;\
${NIGIRI_SDK_DIR}/lib/libtg.a;\
${NIGIRI_SDK_DIR}/lib/librtree.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_base.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_severity.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_malloc_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_raw_logging_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_spinlock_wait.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_strerror.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_throw_delegate.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_hashtablez_sampler.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_raw_hash_set.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_city.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_hash.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_low_level_hash.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_strings.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_strings_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_str_format_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_cord.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_cord_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_cordz_functions.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_cordz_handle.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_cordz_info.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_synchronization.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_graphcycles_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_kernel_timeout_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_time.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_civil_time.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_time_zone.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_int128.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_status.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_statusor.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_globals.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_initialize.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_entry.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_sink.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_check_op.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_conditions.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_format.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_globals.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_log_sink_set.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_message.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_nullguard.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_log_internal_proto.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_die_if_null.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_crc32c.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_crc_cord_state.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_crc_cpu_detect.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_crc_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_commandlineflag.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_commandlineflag_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_config.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_marshalling.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_private_handle_accessor.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_program_name.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_flags_reflection.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_exponential_biased.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_debugging_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_demangle_internal.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_examine_stack.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_leak_check.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_stacktrace.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_symbolize.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_bad_optional_access.a;\
${NIGIRI_SDK_DIR}/lib/libabsl_bad_variant_access.a"
)

# --- pybind11 ---
find_package(pybind11 CONFIG REQUIRED)

# std::thread (reverse-RAPTOR parallelism) needs the platform thread library.
find_package(Threads REQUIRED)

file(GLOB_RECURSE SOURCES
    src/input/*.cpp
    src/data/*.cpp
    src/kernel/*.cpp
    src/pt/*.cpp
    src/geometry/*.cpp
    src/output/*.cpp
    src/heatmap/*.cpp
    src/network/*.cpp
    src/preprocessing/*.cpp
    src/catchment/*.cpp
    src/matrix/*.cpp
    src/pipeline.cpp
)

pybind11_add_module(_routing
    src/pybind_module.cpp
    ${SOURCES}
)

target_include_directories(_routing PRIVATE src)
target_link_libraries(_routing PRIVATE duckdb nigiri Threads::Threads)

install(TARGETS _routing LIBRARY DESTINATION routing)
