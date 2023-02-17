import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";
import styled, { keyframes } from "styled-components";

import fontawesome from "@agir/lib/utils/fontawesome";
import style from "@agir/front/genericComponents/_variables.scss";

import { fontIsLoaded } from "@agir/carte/map/utils";

import INFO_ICON from "@agir/carte/common/images/info-copyright-icon.svg";

const skeleton = keyframes`
  to {
    background-position: 350% 0, 0 0;
  }
`;

const StyledStaticMapBackground = styled.div``;
const StyledAttribution = styled.div``;
const StyledStaticMapWrapper = styled.div`
  width: 100%;
  height: 100%;
  position: relative;
  background-color: lightgrey;
  background-image: linear-gradient(
      100deg,
      rgba(230, 230, 230, 0) 0,
      rgba(230, 230, 230, 1) 50%,
      rgba(230, 230, 230, 0) 100%
    ),
    linear-gradient(rgba(220, 220, 220, 1) 100%, transparent 0%);
  background-size: 33% 100%, 100% 100%;
  background-position: -150% 0, 0 0;
  background-repeat: no-repeat;
  animation: ${skeleton} 2.5s infinite ease-in;
  animation-play-state: ${({ $isLoaded }) =>
    $isLoaded ? "paused" : "running"};

  & > * {
    opacity: ${({ $isLoaded }) => ($isLoaded ? 1 : 0)};
    transition: opacity 300ms ease-in;
  }

  & > ${StyledStaticMapBackground} {
    background-position: center center;
    background-repeat: no-repeat;
    background-size: auto auto;
    height: 100%;
    width: 100%;
    will-change: opacity;
  }

  & > svg {
    position: absolute;
    top: calc(50% - 12px);
    left: 50%;
    transform: translate(-50%, -50%);
    transform-origin: center center;
    width: 2rem;
    height: 2rem;
    opacity: ${({ $isLoaded }) => ($isLoaded ? 1 : 0)};
    transform: translate(-50%, -50%);
    transition: opacity 300ms ease-in;
    will-change: opacity;
  }

  & > svg + svg {
    transform-origin: bottom center;
    transform: translate(-50%, -50%) scale(1, 1);
  }

  ${StyledAttribution} {
    font-size: 12px;
    position: absolute;
    bottom: 3px;
    right: 3px;
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    justify-content: flex-end;
    font-family: Arial, sans-serif;

    ul {
      list-style: none;
      background-color: white;
      padding: 0 5px;
      margin: 0 3px 0 0;
      font-size: 11px;
      line-height: 1.5;
      cursor: default;
    }

    button {
      display: block;
      width: 1rem;
      height: 1rem;
      font-size: 0;
      border: none;
      background-color: none;
      background: url(${INFO_ICON});
      background-repeat: no-repeat;
      background-size: cover;
      opacity: 0.4;
      cursor: pointer;

      &:hover {
        opacity: 0.8;
      }
    }
  }
`;

const StaticMap = (props) => {
  const { staticMapUrl, iconConfiguration, ...rest } = props;

  const [isLoaded, setIsLoaded] = useState(false);
  const [shouldShowAttributions, setShouldShowAttributions] = useState(false);
  const isMounted = useRef(true);
  const toggleAttributions = useCallback(() => {
    setShouldShowAttributions((state) => !state);
  }, []);

  useEffect(() => {
    isMounted.current = true;
    return () => (isMounted.current = false);
  }, []);

  useEffect(() => {
    if (!staticMapUrl) {
      return;
    }
    const image = new Image();
    const handleLoad = async () => {
      try {
        await fontIsLoaded("'Font Awesome 6 Free'");
        isMounted.current && setIsLoaded(true);
      } catch (e) {
        isMounted.current && setIsLoaded(true);
      }
    };
    image.addEventListener("load", handleLoad, false);
    image.src = staticMapUrl;

    return () => {
      image.removeEventListener("load", handleLoad, false);
    };
  }, [staticMapUrl]);

  return (
    <StyledStaticMapWrapper $isLoaded={isLoaded} {...rest}>
      <StyledStaticMapBackground
        style={{ backgroundImage: `url(${staticMapUrl})` }}
      />
      <svg
        width="40"
        height="44"
        viewBox="0 0 40 44"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M19.4125 36.53L19.7578 36.8915L20.1032 36.53L29.8864 26.2879C35.4834 20.4284 35.4342 10.8888 29.7907 4.98059C24.1473 -0.927579 15.035 -0.979031 9.43801 4.88049C3.84101 10.74 3.89016 20.2796 9.53364 26.1878L19.4125 36.53Z"
          fill={
            iconConfiguration?.color
              ? iconConfiguration.color
              : style.secondary500
          }
          stroke={iconConfiguration?.color ? style.white : style.black1000}
          strokeWidth="2px"
        />
        {iconConfiguration?.iconName &&
        fontawesome(iconConfiguration.iconName) ? (
          <text
            x="50%"
            y="16"
            dominantBaseline="central"
            textAnchor="middle"
            fontFamily="'Font Awesome 6 Free'"
            fontSize="16px"
            fill="#FFFFFF"
          >
            {fontawesome(iconConfiguration.iconName)}
          </text>
        ) : null}
      </svg>
      <svg
        width="40"
        height="44"
        viewBox="0 0 40 44"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <ellipse opacity="0.3" cx="20" cy="38" rx="14" ry="5" fill="black" />
      </svg>
      <StyledAttribution>
        {shouldShowAttributions && (
          <ul>
            <li>
              © Contributeurs{" "}
              <a
                href="https://www.openstreetmap.org/copyright"
                target="_blank"
                rel="noopener noreferrer"
              >
                OpenStreetMap
              </a>
            </li>
          </ul>
        )}
        <button type="button" title="Attributions" onClick={toggleAttributions}>
          <span>i</span>
        </button>
      </StyledAttribution>
    </StyledStaticMapWrapper>
  );
};
StaticMap.propTypes = {
  staticMapUrl: PropTypes.string,
  iconConfiguration: PropTypes.shape({
    iconName: PropTypes.string,
    color: PropTypes.string,
    iconUrl: PropTypes.string,
    iconAnchor: PropTypes.string,
  }),
};
export default StaticMap;
