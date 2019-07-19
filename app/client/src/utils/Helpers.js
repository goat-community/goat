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
    )
};

export default helpers;
