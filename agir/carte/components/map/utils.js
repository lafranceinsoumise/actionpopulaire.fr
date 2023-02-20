import FontFaceOnload from "fontfaceonload";

import {
  addQueryStringParams,
  parseQueryStringParams,
} from "@agir/lib/utils/url";

export function getQueryParameterByName(name) {
  const url = window.location.href;
  name = name.replace(/[[\]]/g, "\\$&");
  const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
    results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return "";
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function deepAssign(target, source) {
  for (let key of Object.keys(source)) {
    if (typeof source[key] === "object") {
      if (!(key in target)) {
        target[key] = {};
      }
      deepAssign(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
}

export function element(tag, children = [], attrs = {}) {
  const elem = document.createElement(tag);
  children
    .map((e) => {
      if (e instanceof Element) {
        return e;
      } else if (e.constructor === String) {
        return document.createTextNode(e);
      }
      return element.apply(null, e);
    })
    .forEach((e) => elem.appendChild(e));
  deepAssign(elem, attrs);
  return elem;
}

export function fontIsLoaded(fontName) {
  return new Promise((resolve, reject) =>
    FontFaceOnload(fontName, {
      success: resolve,
      error: reject,
    })
  );
}

export const fontawesomeIsLoaded = async () => {
  await fontIsLoaded("Font Awesome 6 Free");
  await fontIsLoaded("Font Awesome 6 Brands");
  return true;
};

export const ARROW_SIZE = 20;

export const OVERSEAS_COUNTRY_CODE_TO_DEPARTEMENT = {
  GP: "971",
  MQ: "972",
  GF: "973",
  RE: "974",
  PM: "975",
  YT: "976",
  TF: "984",
  WF: "986",
  PF: "987",
  NC: "988",
};

export const getDefaultBoundsForUser = (user) => {
  if (["FR", "BL", "MF"].includes(user?.country) && user?.zip) {
    return JSON.stringify({ code_postal: user.zip });
  }
  if (OVERSEAS_COUNTRY_CODE_TO_DEPARTEMENT[user?.country]) {
    return JSON.stringify({
      departement: OVERSEAS_COUNTRY_CODE_TO_DEPARTEMENT[user?.country],
    });
  }
};

const URLSearchParams = [
  "subtype",
  "include_past",
  "include_hidden",
  "bounds",
  "no_control",
];

export const parseURLSearchParams = () => {
  const currentParams = parseQueryStringParams();
  const newParams = Object.entries(currentParams).reduce(
    (newParams, [key, value]) => {
      if (URLSearchParams.includes(key)) {
        newParams[key] = decodeURIComponent(value);
      }
      return newParams;
    },
    {}
  );

  return newParams;
};

export const getMapUrl = (baseURL, defaultBounds) => {
  const params = parseURLSearchParams();

  if (!params.bounds && defaultBounds) {
    params.bounds = defaultBounds;
  }

  return addQueryStringParams(baseURL, params);
};
