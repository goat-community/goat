create extension plv8;

create table plv8_js_modules (
    module text unique primary key,
    autoload bool default true,
    source text
);

create or replace function plv8_require()
returns void as $$
    moduleCache = {};

    load = function(key, source) {
        var module = {exports: {}};
        eval("(function(module, exports) {" + source + "; })")(module, module.exports);
            
        // store in cache
        moduleCache[key] = module.exports;
        return module.exports;
    };
	
    require = function(module) {
        if(moduleCache[module])
            return moduleCache[module];
        var rows = plv8.execute(
            "select source from plv8_js_modules where module = $1", 
            [module]
        );

        if(rows.length === 0) {
            plv8.elog(NOTICE, 'Could not load module: ' + module);
            return null;
        }

        return load(module, rows[0].source);
    };
    
    // Grab modules worth auto-loading at context start and let them cache
    var query = 'select module, source from plv8_js_modules where autoload = true';
    plv8.execute(query).forEach(function(row) {
        load(row.module, row.source);
    });
$$ language plv8;