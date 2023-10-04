import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import illustration from "./assets/illu-visio.svg";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import StyledCard from "./StyledCard";
import YoutubeEmbed from "./YoutubeEmbed";

const StyledFigure = styled(StyledCard)`
  width: 100%;
  overflow: hidden;
  display: flex;
  gap: 1.5rem 2.5rem;
  padding: 0 1rem 0 2rem;
  align-items: center;
  justify-content: space-between;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: calc(100% - 2.75rem);
    margin: 1rem auto;
    box-shadow: ${(props) => props.theme.cardShadow};
    padding: 2rem 1rem 0;
    flex-flow: column nowrap;
    text-align: center;
  }

  figcaption {
    max-width: 100%;

    & > ${Button} {
      display: inline-flex;
      align-items: center;
      font-weight: 600;
    }

    & > span {
      padding-top: 10px;
      display: block;
      white-space: nowrap;
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 400;
      font-size: 13px;
      line-height: 1.5;
    }
  }
`;

const OnlineUrlCard = (props) => {
  const { onlineUrl, youtubeVideoID, isPast } = props;

  if (youtubeVideoID) {
    return <YoutubeEmbed id={youtubeVideoID} />;
  }

  if (isPast) {
    return null;
  }

  if (onlineUrl) {
    return (
      <StyledFigure as="figure">
        <figcaption>
          <Button
            icon="video"
            link
            href={onlineUrl}
            target="_blank"
            color="secondary"
          >
            Rejoindre en ligne
          </Button>
          <span>{onlineUrl}</span>
        </figcaption>
        <img
          src={illustration}
          alt="visioconference"
          width="255"
          height="145"
        />
      </StyledFigure>
    );
  }
  return null;
};

OnlineUrlCard.propTypes = {
  onlineUrl: PropTypes.string,
  youtubeVideoID: PropTypes.string,
  isPast: PropTypes.bool,
};

export default OnlineUrlCard;
