const helpers = {
  humanize: function humanize(str) {
    return str
      .replace(/^[\s_]+|[\s_]+$/g, "")
      .replace(/[_\s]+/g, " ")
      .replace(/^[a-z]/, function(m) {
        return m.toUpperCase();
      });
  },
  groupBy: (items, key) =>
    items.reduce(
      (result, item) => ({
        ...result,
        [item[key]]: [...(result[item[key]] || []), item]
      }),
      {}
    ),
  debounce: (fn, delay) => {
    let timeoutID = null;
    return function() {
      clearTimeout(timeoutID);
      let args = arguments;
      let that = this;
      timeoutID = setTimeout(function() {
        fn.apply(that, args);
      }, delay);
    };
  }
};

export default helpers;
