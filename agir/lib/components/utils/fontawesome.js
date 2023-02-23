const BINDINGS = {
  "chart-network": {
    fontFamily: "Font Awesome 6 Pro",
    fontWeight: "900",
    content: "\f78a",
  },
};

const fontawesome = (iconName, asObject = false) => {
  if (!iconName || typeof iconName !== "string") {
    return null;
  }

  iconName = iconName.toLowerCase();

  if (!BINDINGS[iconName]) {
    const span = document.createElement("span");
    span.className = `fa fa-${iconName}`;
    document.body.appendChild(span);
    const spanStyle = window.getComputedStyle(span);
    const beforeStyle = window.getComputedStyle(span, ":before");
    const content =
      beforeStyle?.content &&
      !beforeStyle.content.includes("none") &&
      beforeStyle.content.replaceAll('"', "");
    BINDINGS[iconName] = {
      fontFamily: spanStyle.fontFamily,
      fontWeight: spanStyle.fontWeight.replaceAll('"', ""),
      text: content || "",
    };
    document.body.removeChild(span);
  }

  return asObject ? BINDINGS[iconName] : BINDINGS[iconName].text;
};

export default fontawesome;
