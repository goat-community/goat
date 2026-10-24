#pragma once

// Thin RAII wrapper over the stable DuckDB C API (duckdb.h).
//
// The routing module used to link DuckDB's C++ API, which ties the build to
// one libduckdb version's headers (and, from DuckDB 2.0, to headers that are no
// longer shipped). The C API is the stable interface, so everything the module
// needs from DuckDB goes through this file:
//
//   Database / Connection   open an in-memory database, run SQL
//   Result                  query outcome; error state plus chunk iteration
//   DataChunk / Vector      typed, validity-aware column access (no boxing)
//   Appender                row-wise or whole-chunk bulk insert
//
// Only non-deprecated C API functions are used (duckdb_fetch_chunk, not
// duckdb_row_count / duckdb_value_*), so the same sources build against every
// libduckdb whose duckdb.h declares the 1.x stable surface, 1.5.x and 2.0.
//
// Error model, kept from the C++ API this replaces: Connection::Query never
// throws, the returned Result carries the error (callers that ignore a failing
// DROP/SET keep ignoring it). Everything else (open, appender, typed access
// to a NULL or mistyped column) throws duck::Error.

#include <duckdb.h>

#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

namespace routing::duck
{

using idx_t = std::uint64_t;

class Error : public std::runtime_error
{
public:
    using std::runtime_error::runtime_error;
};

// Rows per standard DuckDB vector (what STANDARD_VECTOR_SIZE was). Read once
// from the loaded library, so it always matches the DuckDB actually running.
inline std::size_t vector_size()
{
    static std::size_t const n = static_cast<std::size_t>(duckdb_vector_size());
    return n;
}

namespace detail
{

template <class T> struct TypeOf;
template <> struct TypeOf<bool>          { static constexpr duckdb_type value = DUCKDB_TYPE_BOOLEAN; };
template <> struct TypeOf<std::int8_t>   { static constexpr duckdb_type value = DUCKDB_TYPE_TINYINT; };
template <> struct TypeOf<std::uint8_t>  { static constexpr duckdb_type value = DUCKDB_TYPE_UTINYINT; };
template <> struct TypeOf<std::int16_t>  { static constexpr duckdb_type value = DUCKDB_TYPE_SMALLINT; };
template <> struct TypeOf<std::uint16_t> { static constexpr duckdb_type value = DUCKDB_TYPE_USMALLINT; };
template <> struct TypeOf<std::int32_t>  { static constexpr duckdb_type value = DUCKDB_TYPE_INTEGER; };
template <> struct TypeOf<std::uint32_t> { static constexpr duckdb_type value = DUCKDB_TYPE_UINTEGER; };
template <> struct TypeOf<std::int64_t>  { static constexpr duckdb_type value = DUCKDB_TYPE_BIGINT; };
template <> struct TypeOf<std::uint64_t> { static constexpr duckdb_type value = DUCKDB_TYPE_UBIGINT; };
template <> struct TypeOf<float>         { static constexpr duckdb_type value = DUCKDB_TYPE_FLOAT; };
template <> struct TypeOf<double>        { static constexpr duckdb_type value = DUCKDB_TYPE_DOUBLE; };

char const *type_name(duckdb_type t);

[[noreturn]] void throw_type_mismatch(duckdb_type actual, duckdb_type wanted);
[[noreturn]] void throw_null_access();
[[noreturn]] void throw_unsupported_cast(duckdb_type actual);

inline std::string_view string_view_of(duckdb_string_t const &s)
{
    // Documented duckdb_string_t layout: strings up to 12 bytes live inline.
    std::uint32_t const len = s.value.inlined.length;
    return len <= 12 ? std::string_view(s.value.inlined.inlined, len)
                     : std::string_view(s.value.pointer.ptr, len);
}

} // namespace detail

// Non-owning view of one column of a DataChunk (or the child of a LIST
// column). Valid as long as the chunk it came from. Rows are read by position,
// which assumes a flat vector: Connection::Query materialises its result
// (duckdb_query), and DuckDB scans a materialised result into flat vectors.
// A streaming result could hand out dictionary or constant vectors.
class Vector
{
public:
    Vector() = default;
    explicit Vector(duckdb_vector v);

    duckdb_type type() const { return type_; }

    // Raw typed values, indexed by row. Throws unless the column's physical
    // type is exactly T (a stricter replacement for reinterpret_cast on
    // UnifiedVectorFormat::data). Rows that are NULL hold unspecified values:
    // check is_valid() first.
    template <class T>
    T *data() const
    {
        if (type_ != detail::TypeOf<std::remove_const_t<T>>::value)
            detail::throw_type_mismatch(type_, detail::TypeOf<std::remove_const_t<T>>::value);
        return static_cast<T *>(raw_);
    }

    // Validity mask; null means "every row is valid".
    std::uint64_t *validity() const { return validity_; }
    bool is_valid(idx_t row) const
    {
        return validity_ == nullptr || duckdb_validity_row_is_valid(validity_, row);
    }

    // Value of one row converted to T, like Value::GetValue<T>(): numeric
    // columns convert to any numeric T, VARCHAR columns to std::string.
    // Throws on NULL. For per-row convenience on small results; loops over
    // many rows should take data<T>() once and check is_valid().
    template <class T>
    T get(idx_t row) const
    {
        if (!is_valid(row))
            detail::throw_null_access();
        if constexpr (std::is_same_v<T, std::string>)
        {
            if (type_ != DUCKDB_TYPE_VARCHAR)
                detail::throw_type_mismatch(type_, DUCKDB_TYPE_VARCHAR);
            return std::string(detail::string_view_of(static_cast<duckdb_string_t const *>(raw_)[row]));
        }
        else
        {
            switch (type_)
            {
            case DUCKDB_TYPE_BOOLEAN:   return static_cast<T>(static_cast<bool const *>(raw_)[row]);
            case DUCKDB_TYPE_TINYINT:   return static_cast<T>(static_cast<std::int8_t const *>(raw_)[row]);
            case DUCKDB_TYPE_UTINYINT:  return static_cast<T>(static_cast<std::uint8_t const *>(raw_)[row]);
            case DUCKDB_TYPE_SMALLINT:  return static_cast<T>(static_cast<std::int16_t const *>(raw_)[row]);
            case DUCKDB_TYPE_USMALLINT: return static_cast<T>(static_cast<std::uint16_t const *>(raw_)[row]);
            case DUCKDB_TYPE_INTEGER:   return static_cast<T>(static_cast<std::int32_t const *>(raw_)[row]);
            case DUCKDB_TYPE_UINTEGER:  return static_cast<T>(static_cast<std::uint32_t const *>(raw_)[row]);
            case DUCKDB_TYPE_BIGINT:    return static_cast<T>(static_cast<std::int64_t const *>(raw_)[row]);
            case DUCKDB_TYPE_UBIGINT:   return static_cast<T>(static_cast<std::uint64_t const *>(raw_)[row]);
            case DUCKDB_TYPE_FLOAT:     return static_cast<T>(static_cast<float const *>(raw_)[row]);
            case DUCKDB_TYPE_DOUBLE:    return static_cast<T>(static_cast<double const *>(raw_)[row]);
            default:                    detail::throw_unsupported_cast(type_);
            }
        }
    }

    // VARCHAR column: view of one row's bytes, valid as long as the chunk.
    std::string_view string_at(idx_t row) const
    {
        if (type_ != DUCKDB_TYPE_VARCHAR)
            detail::throw_type_mismatch(type_, DUCKDB_TYPE_VARCHAR);
        return detail::string_view_of(static_cast<duckdb_string_t const *>(raw_)[row]);
    }

    // LIST column access: entry i spans [offset, offset + length) of the
    // child vector, which holds all rows' elements back to back.
    duckdb_list_entry const *list_entries() const
    {
        if (type_ != DUCKDB_TYPE_LIST)
            detail::throw_type_mismatch(type_, DUCKDB_TYPE_LIST);
        return static_cast<duckdb_list_entry const *>(raw_);
    }
    Vector list_child() const;

private:
    duckdb_vector vec_ = nullptr;
    void *raw_ = nullptr;
    std::uint64_t *validity_ = nullptr;
    duckdb_type type_ = DUCKDB_TYPE_INVALID;
};

// Owning data chunk: either one fetched from a Result, or one built with
// create() to bulk-load through Appender::append_chunk.
class DataChunk
{
public:
    DataChunk() = default;
    explicit DataChunk(duckdb_data_chunk c) : chunk_(c) {}
    DataChunk(DataChunk &&o) noexcept : chunk_(o.chunk_) { o.chunk_ = nullptr; }
    DataChunk &operator=(DataChunk &&o) noexcept;
    DataChunk(DataChunk const &) = delete;
    DataChunk &operator=(DataChunk const &) = delete;
    ~DataChunk();

    // Writable chunk with the given column types, vector_size() rows of capacity.
    static DataChunk create(std::initializer_list<duckdb_type> types);

    // False for the "no more rows" chunk returned at the end of a Result.
    explicit operator bool() const { return chunk_ != nullptr; }

    idx_t size() const { return duckdb_data_chunk_get_size(chunk_); }
    void set_size(idx_t n) { duckdb_data_chunk_set_size(chunk_, n); }
    idx_t column_count() const { return duckdb_data_chunk_get_column_count(chunk_); }
    Vector column(idx_t i) const { return Vector(duckdb_data_chunk_get_vector(chunk_, i)); }
    // Empty the chunk for refilling. Column data pointers may change:
    // re-fetch them from column(i).data<T>() afterwards.
    void reset() { duckdb_data_chunk_reset(chunk_); }

    duckdb_data_chunk raw() const { return chunk_; }

private:
    duckdb_data_chunk chunk_ = nullptr;
};

// Outcome of one statement. Move-only; destroys the C result on scope exit.
class Result
{
public:
    Result();
    Result(Result &&o) noexcept;
    Result &operator=(Result &&o) noexcept;
    Result(Result const &) = delete;
    Result &operator=(Result const &) = delete;
    ~Result();

    bool HasError() const;
    std::string GetError() const;
    duckdb_result *raw() { return &res_; }

    // Next chunk of rows; an empty (falsy) chunk once exhausted. The chunk
    // size is not the result size: loop until the chunk is falsy and skip
    // chunks with size() == 0.
    DataChunk Fetch();

    // The only value of a 1x1 result (count(*) and the like): consumes the
    // first chunk. Throws on an empty result or a NULL.
    template <class T>
    T scalar()
    {
        DataChunk chunk = Fetch();
        if (!chunk || chunk.size() == 0)
            throw Error("DuckDB result has no rows");
        return chunk.column(0).get<T>(0);
    }

private:
    duckdb_result res_;
};

class Database
{
public:
    // In-memory database when path is null (the only mode used here).
    explicit Database(char const *path = nullptr);
    Database(Database const &) = delete;
    Database &operator=(Database const &) = delete;
    ~Database();

    duckdb_database raw() const { return db_; }

private:
    duckdb_database db_ = nullptr;
};

class Connection
{
public:
    explicit Connection(Database &db);
    Connection(Connection const &) = delete;
    Connection &operator=(Connection const &) = delete;
    ~Connection();

    // Run SQL (several statements allowed: the last one's result is returned).
    // Never throws for a failing statement; inspect the Result.
    Result Query(std::string const &sql);

    duckdb_connection raw() const { return con_; }

private:
    duckdb_connection con_ = nullptr;
};

// Bulk insert into an existing table (temp tables included). Destruction
// flushes and closes, ignoring errors; call close() where a flush failure
// must surface. Not thread-safe.
class Appender
{
public:
    Appender(Connection &con, std::string const &table);
    Appender(Appender const &) = delete;
    Appender &operator=(Appender const &) = delete;
    ~Appender();

    // Row-wise API: begin_row, one append per column, end_row. Each append
    // casts to the column's type, as the C++ Appender did.
    void begin_row() { check(duckdb_appender_begin_row(app_)); }
    void end_row() { check(duckdb_appender_end_row(app_)); }
    void append(bool v) { check(duckdb_append_bool(app_, v)); }
    void append(std::int8_t v) { check(duckdb_append_int8(app_, v)); }
    void append(std::uint8_t v) { check(duckdb_append_uint8(app_, v)); }
    void append(std::int16_t v) { check(duckdb_append_int16(app_, v)); }
    void append(std::uint16_t v) { check(duckdb_append_uint16(app_, v)); }
    void append(std::int32_t v) { check(duckdb_append_int32(app_, v)); }
    void append(std::uint32_t v) { check(duckdb_append_uint32(app_, v)); }
    void append(std::int64_t v) { check(duckdb_append_int64(app_, v)); }
    void append(std::uint64_t v) { check(duckdb_append_uint64(app_, v)); }
    void append(float v) { check(duckdb_append_float(app_, v)); }
    void append(double v) { check(duckdb_append_double(app_, v)); }
    void append(std::string_view v) { check(duckdb_append_varchar_length(app_, v.data(), v.size())); }
    void append(std::string const &v) { append(std::string_view(v)); }
    void append(char const *v) { append(std::string_view(v)); }
    void append_null() { check(duckdb_append_null(app_)); }

    template <class... Args>
    void append_row(Args const &...args)
    {
        begin_row();
        (append(args), ...);
        end_row();
    }

    // Whole-chunk API: fill a DataChunk::create()d chunk, set_size(n), append.
    // The chunk is not modified; reset() it before refilling.
    void append_chunk(DataChunk &chunk) { check(duckdb_append_data_chunk(app_, chunk.raw())); }

    void flush() { check(duckdb_appender_flush(app_)); }
    // Flush and close; throws if the flush fails. The destructor then only
    // releases the handle.
    void close();

private:
    void check(duckdb_state s) const
    {
        if (s != DuckDBSuccess)
            fail();
    }
    [[noreturn]] void fail() const;

    duckdb_appender app_ = nullptr;
};

} // namespace routing::duck
