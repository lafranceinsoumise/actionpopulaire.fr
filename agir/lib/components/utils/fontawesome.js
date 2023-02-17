const BINDINGS = {};

const fontawesome = (iconName) => {
  if (!iconName || typeof iconName !== "string") {
    return "";
  }

  iconName = iconName.toLowerCase();

  if (!BINDINGS[iconName]) {
    BINDINGS[iconName] = document.createElement("span");
    BINDINGS[iconName].className = `fa fa-${iconName}`;
  }

  const span = BINDINGS[iconName];
  document.body.appendChild(span);
  let unicode = window.getComputedStyle(span, ":before").content;
  document.body.removeChild(span);

  return unicode && unicode.slice(1, -1);
};

export default fontawesome;
