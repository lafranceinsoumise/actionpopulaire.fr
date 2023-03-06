export const getScrollableParent = (element) => {
  if (element === window) {
    return element;
  }

  const regex = /(auto|scroll)/;
  const parents = (_node, ps) => {
    if (_node.parentNode === null) {
      return ps;
    }
    return parents(_node.parentNode, ps.concat([_node]));
  };

  const style = (_node, prop) =>
    getComputedStyle(_node, null).getPropertyValue(prop);
  const overflow = (_node) =>
    style(_node, "overflow") +
    style(_node, "overflow-y") +
    style(_node, "overflow-x");
  const scroll = (_node) => regex.test(overflow(_node));

  const scrollParent = (_node) => {
    if (!(_node instanceof HTMLElement || _node instanceof SVGElement)) {
      return;
    }

    const ps = parents(_node.parentNode, []);

    for (let i = 0; i < ps.length; i += 1) {
      if (scroll(ps[i])) {
        return ps[i];
      }
    }

    return document.scrollingElement || document.documentElement;
  };

  return scrollParent(element);
};

const INTERACTIVE_ELEMENT = {
  A: (element) => element.hasAttribute("href"),
  AUDIO: (element) => element.hasAttribute("controls"),
  BUTTON: true,
  DETAILS: true,
  EMBED: true,
  IFRAME: true,
  KEYGEN: true,
  LABEL: true,
  SELECT: true,
  TEXTAREA: true,
  VIDEO: (element) => element.hasAttribute("controls"),
};

export function isInteractiveElement(element) {
  const { nodeName } = element;
  if (element instanceof HTMLInputElement && element.type !== "hidden") {
    return true;
  }
  if (element.hasAttribute("tabindex") && element.tabIndex > -1) {
    return true;
  }
  if (!INTERACTIVE_ELEMENT[nodeName]) {
    return false;
  }
  if (typeof INTERACTIVE_ELEMENT[nodeName] === "function") {
    return INTERACTIVE_ELEMENT[nodeName](element);
  }
  return INTERACTIVE_ELEMENT[nodeName] === true;
}

export const handleEventExceptForInteractiveChild = (event, callback) => {
  if (!callback) {
    return;
  }
  for (
    let target = event.target;
    target !== event.currentTarget;
    target = target.parentElement
  ) {
    if (isInteractiveElement(target)) {
      return;
    }
  }
  callback(event);
};
