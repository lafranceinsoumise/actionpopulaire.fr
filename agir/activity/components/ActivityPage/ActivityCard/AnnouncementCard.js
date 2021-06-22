import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import GenericCardContainer from "./GenericCardContainer";

const StyledContent = styled.p`
  display: flex;
  flex-flow: column nowrap;
  justify-content: flex-start;
  width: 100%;
  margin: 0;

  & > * {
    margin: 0;
  }

  & > a > img {
    width: 100%;
    height: auto;
    margin-bottom: 1rem;

    @media (max-width: ${style.collapse}px) {
      border-radius: ${style.borderRadius};
    }
  }

  & > div {
    margin: 0.5rem 0;

    & > p {
      margin-bottom: 0.5rem;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
`;

const AnnouncementCard = (props) => {
  const { image, title, content, link, linkLabel } = props;
  return (
    <GenericCardContainer {...props}>
      <StyledContent>
        {image?.activity && (
          <a href={link} aria-label={linkLabel}>
            <img src={image.activity} width="548" height="241" />
          </a>
        )}
        <strong style={{ fontWeight: 600 }}>{title}</strong>
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </StyledContent>
    </GenericCardContainer>
  );
};

AnnouncementCard.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  link: PropTypes.string,
  linkLabel: PropTypes.string,
  content: PropTypes.string.isRequired,
  image: PropTypes.shape({
    activity: PropTypes.string,
  }),
  startDate: PropTypes.string,
  endDate: PropTypes.string,
  priority: PropTypes.number,
  activityId: PropTypes.number,
  customDisplay: PropTypes.string,
  config: PropTypes.shape({
    icon: PropTypes.string,
  }),
  status: PropTypes.string,
};
export default AnnouncementCard;
