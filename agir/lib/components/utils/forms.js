export const objectToFormData = (obj, rootName, ignoreList) => {
  var formData = new FormData();
  const appendFormData = (data, root) => {
    if (Array.isArray(ignoreList) && ignoreList.includes(root)) {
      return;
    }

    root = root || "";

    if (data instanceof File) {
      formData.append(root, data);
      return;
    }

    if (Array.isArray(data)) {
      for (var i = 0; i < data.length; i++) {
        appendFormData(data[i], root + "[" + i + "]");
      }
      return;
    }

    if (typeof data === "object" && data) {
      for (var key in data) {
        if (data.hasOwnProperty(key)) {
          if (root === "") {
            appendFormData(data[key], key);
          } else {
            appendFormData(data[key], root + "." + key);
          }
        }
      }
      return;
    }

    if (data !== null && typeof data !== "undefined") {
      formData.append(root, data);
    }
  };

  appendFormData(obj, rootName);

  return formData;
};
