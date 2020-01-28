/**
 * URL related util methods
 */
const UrlUtil = {
  /**
   * Returns all query params of the given search part (querySearch) of an URL
   * as JS object (key-value).
   * If querySearch is not provided it is derived from the current location.
   *
   * @param  {String} querySearch Search part (querySearch) of an URL
   * @return {Object}             Key-value pairs of the URL parameters
   */
  getQueryParams(querySearch) {
    if (!querySearch) {
      querySearch = document.location.search;
    }
    querySearch = querySearch.split("+").join(" ");

    const re = /[?&]?([^=]+)=([^&]*)/g;
    let params = {};
    let tokens;
    while ((tokens = re.exec(querySearch))) {
      params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }

    return params;
  },

  /**
   * Returns a dedicated URL parameter if existing.
   * If querySearch is not provided it is derived from the current location.
   *
   * @param  {String} param       The URL param name
   * @param  {String} querySearch Search part (querySearch) of an URL
   * @return {String}             Value of the given URL param
   */
  getQueryParam(param, querySearch) {
    const params = this.getQueryParams(querySearch);
    let value;
    Object.keys(params).forEach(key => {
      if (key === param) {
        value = params[key];
        return;
      }
    });

    return value;
  }
};

export default UrlUtil;
