import React, { useMemo } from "react";
import styled from "styled-components";

import fontawesome from "@agir/lib/utils/fontawesome";
import style from "@agir/front/genericComponents/_variables.scss";

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
  "chart-network",
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
  "stroopwafel",
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

const StyledPage = styled.main`
  padding: 1.5rem 1rem;
  margin: 0 auto;
  max-width: 992px;
  width: 100%;
  display: grid;
  font-size: 0.875rem;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));

  figure {
    display: flex;
    align-items: stretch;
    margin: 0;
    padding: 0;

    figcaption {
      a {
        line-height: 32px;
        color: inherit;
      }
    }
  }
`;

const Icon = ({ icon }) => {
  const iconConfig = fontawesome(icon, true);
  return (
    <figure>
      <svg
        width="40"
        height="44"
        viewBox="0 0 40 44"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M19.4125 36.53L19.7578 36.8915L20.1032 36.53L29.8864 26.2879C35.4834 20.4284 35.4342 10.8888 29.7907 4.98059C24.1473 -0.927579 15.035 -0.979031 9.43801 4.88049C3.84101 10.74 3.89016 20.2796 9.53364 26.1878L19.4125 36.53Z"
          fill={style.primary500}
          stroke="white"
          strokeWidth="2px"
        />
        <text
          x="50%"
          y="16"
          dominantBaseline="central"
          textAnchor="middle"
          fontFamily={iconConfig?.fontFamily}
          fontWeight={iconConfig?.fontWeight}
          fontSize="16px"
          fill="#FFFFFF"
        >
          {iconConfig.text}
        </text>
      </svg>
      <figcaption>
        <span className={iconConfig.className} />
        &ensp;
        <a
          href={`https://fontawesome.com/icons/${icon}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          {icon}
        </a>
      </figcaption>
    </figure>
  );
};

export const FaIcons = () => {
  const icons = useMemo(() => {
    const dataElement = document.getElementById("usedIcons");
    return dataElement && dataElement.type === "application/json"
      ? JSON.parse(dataElement.textContent).filter(Boolean)
      : usedIcons;
  }, []);

  return (
    <StyledPage>
      {icons.sort().map((icon) => (
        <Icon key={icon} icon={icon} />
      ))}
    </StyledPage>
  );
};

export default FaIcons;
