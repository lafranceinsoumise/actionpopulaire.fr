import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

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

    @media (max-width: ${(props) => props.theme.collapse}px) {
      border-radius: ${(props) => props.theme.borderRadius};
    }
  }

  & > span {
    display: block;
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
  const { activityId, image, title, content, link, linkLabel } = props;
  return (
    <GenericCardContainer {...props} id={activityId} onClick={undefined}>
      <StyledContent>
        {image?.activity && (
          <a href={link} aria-label={linkLabel}>
            <img src={image.activity} width="548" height="241" />
          </a>
        )}
        <strong style={{ fontWeight: 600 }}>{title}</strong>
        <span dangerouslySetInnerHTML={{ __html: content }} />
      </StyledContent>
    </GenericCardContainer>
  );
};

AnnouncementCard.propTypes = {
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
