#include "duck.h"

#include <cstring>

namespace routing::duck
{

namespace detail
{

char const *type_name(duckdb_type t)
{
    switch (t)
    {
    case DUCKDB_TYPE_BOOLEAN:   return "BOOLEAN";
    case DUCKDB_TYPE_TINYINT:   return "TINYINT";
    case DUCKDB_TYPE_SMALLINT:  return "SMALLINT";
    case DUCKDB_TYPE_INTEGER:   return "INTEGER";
    case DUCKDB_TYPE_BIGINT:    return "BIGINT";
    case DUCKDB_TYPE_UTINYINT:  return "UTINYINT";
    case DUCKDB_TYPE_USMALLINT: return "USMALLINT";
    case DUCKDB_TYPE_UINTEGER:  return "UINTEGER";
    case DUCKDB_TYPE_UBIGINT:   return "UBIGINT";
    case DUCKDB_TYPE_FLOAT:     return "FLOAT";
    case DUCKDB_TYPE_DOUBLE:    return "DOUBLE";
    case DUCKDB_TYPE_VARCHAR:   return "VARCHAR";
    case DUCKDB_TYPE_LIST:      return "LIST";
    case DUCKDB_TYPE_ARRAY:     return "ARRAY";
    case DUCKDB_TYPE_STRUCT:    return "STRUCT";
    default:                    return "(other)";
    }
}

void throw_type_mismatch(duckdb_type actual, duckdb_type wanted)
{
    throw Error(std::string("DuckDB column type mismatch: column is ") +
                type_name(actual) + ", code expects " + type_name(wanted));
}

void throw_null_access()
{
    throw Error("DuckDB value is NULL where the code requires a value");
}

void throw_unsupported_cast(duckdb_type actual)
{
    throw Error(std::string("DuckDB column of type ") + type_name(actual) +
                " cannot be read as a number");
}

} // namespace detail

// ── Vector ──────────────────────────────────────────────────────────────

Vector::Vector(duckdb_vector v)
    : vec_(v),
      raw_(duckdb_vector_get_data(v)),
      validity_(duckdb_vector_get_validity(v))
{
    duckdb_logical_type lt = duckdb_vector_get_column_type(v);
    type_ = duckdb_get_type_id(lt);
    duckdb_destroy_logical_type(&lt);
}

Vector Vector::list_child() const
{
    if (type_ != DUCKDB_TYPE_LIST)
        detail::throw_type_mismatch(type_, DUCKDB_TYPE_LIST);
    return Vector(duckdb_list_vector_get_child(vec_));
}

// ── DataChunk ───────────────────────────────────────────────────────────

DataChunk &DataChunk::operator=(DataChunk &&o) noexcept
{
    if (this != &o)
    {
        if (chunk_)
            duckdb_destroy_data_chunk(&chunk_);
        chunk_ = o.chunk_;
        o.chunk_ = nullptr;
    }
    return *this;
}

DataChunk::~DataChunk()
{
    if (chunk_)
        duckdb_destroy_data_chunk(&chunk_);
}

DataChunk DataChunk::create(std::initializer_list<duckdb_type> types)
{
    std::vector<duckdb_logical_type> lts;
    lts.reserve(types.size());
    for (auto t : types)
        lts.push_back(duckdb_create_logical_type(t));
    duckdb_data_chunk c = duckdb_create_data_chunk(lts.data(), lts.size());
    for (auto &lt : lts)
        duckdb_destroy_logical_type(&lt);
    if (!c)
        throw Error("Failed to create DuckDB data chunk");
    return DataChunk(c);
}

// ── Result ──────────────────────────────────────────────────────────────

Result::Result()
{
    std::memset(&res_, 0, sizeof(res_));
}

Result::Result(Result &&o) noexcept : res_(o.res_)
{
    std::memset(&o.res_, 0, sizeof(o.res_));
}

Result &Result::operator=(Result &&o) noexcept
{
    if (this != &o)
    {
        duckdb_destroy_result(&res_);
        res_ = o.res_;
        std::memset(&o.res_, 0, sizeof(o.res_));
    }
    return *this;
}

Result::~Result()
{
    duckdb_destroy_result(&res_);
}

bool Result::HasError() const
{
    return duckdb_result_error(const_cast<duckdb_result *>(&res_)) != nullptr;
}

std::string Result::GetError() const
{
    char const *e = duckdb_result_error(const_cast<duckdb_result *>(&res_));
    return e ? std::string(e) : std::string();
}

DataChunk Result::Fetch()
{
    return DataChunk(duckdb_fetch_chunk(res_));
}

// ── Database / Connection ───────────────────────────────────────────────

Database::Database(char const *path)
{
    char *err = nullptr;
    if (duckdb_open_ext(path, &db_, nullptr, &err) != DuckDBSuccess)
    {
        std::string msg = err ? err : "unknown error";
        if (err)
            duckdb_free(err);
        throw Error("Failed to open DuckDB database: " + msg);
    }
}

Database::~Database()
{
    if (db_)
        duckdb_close(&db_);
}

Connection::Connection(Database &db)
{
    if (duckdb_connect(db.raw(), &con_) != DuckDBSuccess)
        throw Error("Failed to connect to DuckDB database");
}

Connection::~Connection()
{
    if (con_)
        duckdb_disconnect(&con_);
}

Result Connection::Query(std::string const &sql)
{
    Result r;
    // On failure duckdb_query still fills the result with the error message.
    duckdb_query(con_, sql.c_str(), r.raw());
    return r;
}

// ── Appender ────────────────────────────────────────────────────────────

namespace
{
    // The appender's error text (duckdb_appender_error is deprecated).
    std::string error_message(duckdb_appender app)
    {
        duckdb_error_data data = duckdb_appender_error_data(app);
        if (!data)
            return {};
        char const *e = duckdb_error_data_message(data);
        std::string msg = e ? e : "";
        duckdb_destroy_error_data(&data);
        return msg;
    }
} // namespace

Appender::Appender(Connection &con, std::string const &table)
{
    if (duckdb_appender_create(con.raw(), nullptr, table.c_str(), &app_) != DuckDBSuccess)
    {
        std::string msg;
        if (app_)
        {
            msg = error_message(app_);
            duckdb_appender_destroy(&app_);
        }
        throw Error("Failed to create DuckDB appender for '" + table + "': " + msg);
    }
}

Appender::~Appender()
{
    if (app_)
        duckdb_appender_destroy(&app_);
}

void Appender::close()
{
    check(duckdb_appender_close(app_));
}

void Appender::fail() const
{
    std::string msg = error_message(app_);
    throw Error("DuckDB appender error: " + (msg.empty() ? std::string("unknown") : msg));
}

} // namespace routing::duck
