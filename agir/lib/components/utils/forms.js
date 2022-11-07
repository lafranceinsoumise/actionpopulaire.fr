export const objectToFormData = (obj, rootName, ignoreList) => {
  var formData = new FormData();
  const appendFormData = (data, rootProp) => {
    if (Array.isArray(ignoreList) && ignoreList.includes(rootProp)) {
      return;
    }

    rootProp = rootProp || "";

    if (data instanceof File) {
      formData.append(rootProp, data);
      return;
    }

    if (Array.isArray(data)) {
      for (var i = 0; i < data.length; i++) {
        appendFormData(data[i], rootProp + "[" + i + "]");
      }
      return;
    }

    if (typeof data === "object" && data) {
      for (var key in data) {
        if (data.hasOwnProperty(key)) {
          if (rootProp === "") {
            appendFormData(data[key], key);
          } else {
            appendFormData(data[key], rootProp + "." + key);
          }
        }
      }
      return;
    }

    if (data !== null && typeof data !== "undefined") {
      formData.append(rootProp, data);
    }
  };

  appendFormData(obj, rootName);

  return formData;
};
