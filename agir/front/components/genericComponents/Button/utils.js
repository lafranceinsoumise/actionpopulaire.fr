import { icons } from "feather-icons";

export const ICONS = icons;
export const getIconDataUrl =
  ({
    color = "black",
    fill,
    width,
    height,
    strokeWidth,
    strokeLineCap,
    strokeLineJoin,
  }) =>
  ({ icon }) => {
    const svg = ICONS[icon]
      ? ICONS[icon]
          .toSvg({
            width,
            height,
            strokeWidth,
            strokeLineCap,
            strokeLineJoin,
            color: encodeURI(color),
            fill: fill ? "currentColor" : "none",
          })
          .replace(/#/g, "%23")
      : "";
    return svg && `url('data:image/svg+xml;utf8,${svg}')`;
  };
