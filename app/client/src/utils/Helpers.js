import jwt_decode from "jwt-decode";

export function humanize(str) {
  if (!str) return "";
  return str
    .replace(/^[\s_]+|[\s_]+$/g, "")
    .replace(/[_\s]+/g, " ")
    .replace(/^[a-z]/, function(m) {
      return m.toUpperCase();
    });
}

export function groupBy(items, key) {
  return items.reduce(
    (result, item) => ({
      ...result,
      [item[key]]: [...(result[item[key]] || []), item]
    }),
    {}
  );
}

export function getNestedProperty(obj, key) {
  return key.split(".").reduce(function(o, x) {
    return typeof o == "undefined" || o === null ? o : o[x];
  }, obj);
}

export function validateToken(jwtToken) {
  if (!jwtToken) {
    return null;
  }
  const decodedToken = jwt_decode(jwtToken);
  if (
    decodedToken &&
    decodedToken.exp &&
    Date.now() >= decodedToken.exp * 1000
  ) {
    return null;
  } else {
    return decodedToken;
  }
}

export function errorMessage(context, response, mutationType) {
  if (response.status === 500) {
    context.commit(mutationType, "Server problem!");
  } else if (response.data.detail) {
    context.commit(mutationType, response.data.detail);
  } else if (response.data.msg) {
    context.commit(mutationType, response.data.msg);
  }
}

export function addProps(obj, arr, val) {
  if (typeof arr == "string") arr = arr.split(".");

  obj[arr[0]] = obj[arr[0]] || {};

  var tmpObj = obj[arr[0]];

  if (arr.length > 1) {
    arr.shift();
    addProps(tmpObj, arr, val);
  } else obj[arr[0]] = val;

  return obj;
}

export function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

export function debounce(fn, delay) {
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

export function getCurrentDate() {
  const today = new Date();
  return (
    today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate()
  );
}

export function getCurrentTime() {
  const today = new Date();
  return today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds();
}

/**
 * Takes a hex value and prepends a zero if it's a single digit.
 * @param {string} hex Hex value to prepend if single digit.
 * @return {string} hex value prepended with zero if it was single digit,
 *     otherwise the same value that was passed in.
 * @hidden
 */
export function colorZeroPadding(hex) {
  return hex.length == 1 ? `0${hex}` : hex;
}

const iconUnicodeCache = {};

export const getIconUnicode = iconClass => {
  if (iconUnicodeCache[iconClass]) return iconUnicodeCache[iconClass];
  const tempElement = document.createElement("i");
  tempElement.className = iconClass;
  document.body.appendChild(tempElement);
  const character = window
    .getComputedStyle(tempElement, ":before")
    .getPropertyValue("content")
    .replaceAll(`"`, "");
  tempElement.remove();
  if (character) {
    iconUnicodeCache[iconClass] = character;
  }
  return character;
};

/**
 * Converts a color from RGB to hex representation.
 * @param {number[]} rgb rgb representation of the color.
 * @return {string} hex representation of the color.
 * @hidden
 */
export function rgbArrayToHex(rgb) {
  const r = rgb[0];
  const g = rgb[1];
  const b = rgb[2];
  if (r != (r & 255) || g != (g & 255) || b != (b & 255)) {
    throw Error(`"(${r},${g},${b})" is not a valid RGB color`);
  }
  const hexR = colorZeroPadding(r.toString(16));
  const hexG = colorZeroPadding(g.toString(16));
  const hexB = colorZeroPadding(b.toString(16));
  return `#${hexR}${hexG}${hexB}`;
}

// helper function to detect a CSS color
// Taken from Vuetify sources
// https://github.com/vuetifyjs/vuetify/blob/master/packages/vuetify/src/mixins/colorable.ts
export function isCssColor(color) {
  return !!color && !!color.match(/^(#|(rgb|hsl)a?\()/);
}

export function linearInterpolation(x1, x2, y1, y2, x) {
  return (x - x1) * ((y2 - y1) / (x2 - x1)) + y1;
}

// Returns two closest values from the array. If value exist undefined is returned
export function getClosest(a, x) {
  var min = Math.min.apply(null, a),
    max = Math.max.apply(null, a),
    i,
    len;

  if (x < min) {
    // if x is lower than the lowest value
    return min;
  } else if (x > max) {
    // if x is greater than the 'greatest' value
    return max;
  }
  a.sort();
  for (i = 0, len = a.length; i < len; i++) {
    if (x > a[i] && x < a[i + 1]) {
      return [a[i], a[i + 1]];
    }
  }
}

// Returns a single rgb color interpolation between given rgb color
// based on the factor given; via https://codepen.io/njmcode/pen/axoyD?editors=0010
export function interpolateColor(color1, color2, factor) {
  if (arguments.length < 3) {
    factor = 0.5;
  }
  color1 = color1.match(/\d+/g).map(Number);
  color2 = color2.match(/\d+/g).map(Number);
  var result = color1.slice();
  for (var i = 0; i < 3; i++) {
    result[i] = Math.round(result[i] + factor * (color2[i] - color1[i]));
  }
  return `rgb(${result.toString()})`;
}

//https://gist.github.com/maxwells/8251275
export const ColorObj = function(hexOrObject, alpha) {
  var obj;
  if (hexOrObject instanceof Object) {
    obj = hexOrObject;
  } else {
    obj = LinearColorInterpolator.convertHexToRgb(hexOrObject);
  }
  this.r = obj.r;
  this.g = obj.g;
  this.b = obj.b;
  this.alpha = alpha;
};
ColorObj.prototype.asRgbCss = function() {
  if (this.alpha) {
    return (
      "rgba(" + this.r + ", " + this.g + ", " + this.b + ", " + this.alpha + ")"
    );
  } else {
    return "rgb(" + this.r + ", " + this.g + ", " + this.b + ")";
  }
};

export const LinearColorInterpolator = {
  // convert 6-digit hex to rgb components;
  // accepts with or without hash ("335577" or "#335577")
  convertHexToRgb: function(hex, alpha) {
    const match = hex.replace(/#/, "").match(/.{1,2}/g);
    return new ColorObj(
      {
        r: parseInt(match[0], 16),
        g: parseInt(match[1], 16),
        b: parseInt(match[2], 16)
      },
      alpha
    );
  },
  // left and right are colors that you're aiming to find
  // a color between. Percentage (0-100) indicates the ratio
  // of right to left. Higher percentage means more right,
  // lower means more left.
  findColorBetween: function(left, right, percentage) {
    let newColor = {};
    let components = ["r", "g", "b"];
    for (var i = 0; i < components.length; i++) {
      let c = components[i];
      newColor[c] = Math.round(
        left[c] + ((right[c] - left[c]) * percentage) / 100
      );
    }
    return new ColorObj(newColor);
  }
};
