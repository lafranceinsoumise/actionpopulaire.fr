import fontawesome from "@agir/lib/utils/fontawesome";
import React from "react";

export default {
  component: "Fontawesome",
  title: "Generic/Fontawesome",
};

const usedIcons = [
  "arrow-left",
  "arrow-right",
  "arrow-up",
  "bars",
  "bicycle",
  "bolt",
  "book",
  "bug",
  "bullhorn",
  "bus",
  "building",
  "calendar",
  "car",
  "cog",
  "comment",
  "comments",
  "copy",
  "credit-card",
  "cutlery",
  "desktop",
  "download",
  "edit",
  "envelope",
  "envelope-open",
  "exclamation",
  "external-link",
  "film",
  "flag",
  "futbol-o",
  "glass",
  "globe",
  "graduation-cap",
  "handshake-o",
  "heart",
  "industry",
  "info",
  "info-circle",
  "link",
  "long-arrow-right",
  "map",
  "map-marker",
  "pagelines",
  "paint-brush",
  "pencil",
  "phone",
  "plane",
  "plus",
  "refresh",
  "search",
  "star-half",
  "star-half-o",
  "tint",
  "trash",
  "truck",
  "thumb-tack",
  "tv",
  "undo",
  "university",
  "user-circle",
  "users",
  "warning",
];

export const Icons = () => {
  return (
    <div
      style={{
        padding: "1rem",
        margin: 0,
        maxWidth: "992px",
        width: "100%",
        display: "grid",
        fontSize: "0.875rem",
        gridTemplateColumns: "repeat( auto-fit, minmax(180px, 1fr))",
      }}
    >
      {usedIcons.sort().map((icon) => (
        <figure
          key={icon}
          style={{
            display: "flex",
            alignItems: "stretch",
            margin: 0,
            padding: 0,
          }}
        >
          <svg
            width="40"
            height="44"
            viewBox="0 0 40 44"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M19.4125 36.53L19.7578 36.8915L20.1032 36.53L29.8864 26.2879C35.4834 20.4284 35.4342 10.8888 29.7907 4.98059C24.1473 -0.927579 15.035 -0.979031 9.43801 4.88049C3.84101 10.74 3.89016 20.2796 9.53364 26.1878L19.4125 36.53Z"
              fill="#e93a55"
              stroke="white"
              strokeWidth="2px"
            />
            <text
              x="50%"
              y="16"
              dominantBaseline="central"
              textAnchor="middle"
              fontFamily="FontAwesome"
              fontSize="16px"
              fill="#FFFFFF"
            >
              {fontawesome(icon)}
            </text>
          </svg>
          <figcaption>
            <a
              href={`https://fontawesome.com/v4.7/icon/${icon}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{ lineHeight: "32px", color: "inherit" }}
            >
              {icon}
            </a>
          </figcaption>
        </figure>
      ))}
    </div>
  );
};
