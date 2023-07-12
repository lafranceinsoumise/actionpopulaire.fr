import parsePhoneNumber from "libphonenumber-js";
import { validate } from "validate.js";

validate.formatters.cleanMessage = (errors) => {
  const result = {};
  const formattedError = errors.reverse().reduce(
    (obj, error) => ({
      ...obj,
      [error.attribute]: error && error.error,
    }),
    {},
  );
  for (var i in formattedError) {
    var keys = i.split(".");
    keys.reduce(function (r, e, j) {
      return (
        r[e] ||
        (r[e] = isNaN(Number(keys[j + 1]))
          ? keys.length - 1 == j
            ? formattedError[i]
            : {}
          : [])
      );
    }, result);
  }
  return result;
};

validate.extend(validate.validators.datetime, {
  parse: (value) => {
    return new Date(value).valueOf();
  },
  format: (value) => {
    return new Date(value).toISOString();
  },
});

validate.validators.phone = (value, { message }) => {
  let phoneNumber;
  try {
    phoneNumber = parsePhoneNumber(value, "FR");
  } catch (e) {
    return message;
  }
  if (phoneNumber && !phoneNumber.isValid()) {
    return message;
  }
};

validate.validators.optionalUrl = function (
  value,
  options,
  attribute,
  attributes,
) {
  if (validate.isEmpty(value)) {
    return;
  }
  return validate.validators.url(value, options, attribute, attributes);
};

export default validate;
