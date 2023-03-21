const BINDINGS = {};

const prefixClassName = (className) => {
  if (!className || typeof className !== "string") {
    return "fa";
  }
  className = className.toLowerCase().trim();
  if (/^fa-/.test(className)) {
    return className;
  }
  return `fa-${className}`;
};

const fontawesome = (icon, asObject = false) => {
  if (!icon || typeof icon !== "string") {
    return null;
  }

  if (!BINDINGS[icon]) {
    const [iconName, iconStyle = ""] = icon.toLowerCase().split(":");
    const span = document.createElement("span");
    span.className = [
      prefixClassName(iconStyle),
      prefixClassName(iconName),
    ].join(" ");
    document.body.appendChild(span);
    const spanStyle = window.getComputedStyle(span);
    const beforeStyle = window.getComputedStyle(span, ":before");
    const content =
      beforeStyle?.content &&
      !beforeStyle.content.includes("none") &&
      beforeStyle.content.replace(new RegExp('"', "g"), "");
    BINDINGS[icon] = {
      fontFamily: spanStyle.fontFamily,
      fontWeight: spanStyle.fontWeight.replace(new RegExp('"', "g"), ""),
      text: content || "",
      className: span.className,
    };
    document.body.removeChild(span);
  }

  return asObject ? BINDINGS[icon] : BINDINGS[icon].text;
};

export default fontawesome;
