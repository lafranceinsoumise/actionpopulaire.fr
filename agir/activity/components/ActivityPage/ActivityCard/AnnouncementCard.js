import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledCard = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  padding: 0 0 1.5rem;

  @media (max-width: ${style.collapse}px) {
    background-color: ${style.white};
    padding: 1rem 1.5rem 1.5rem 1rem;
    box-shadow: ${style.elaborateShadow};
  }

  article {
    display: flex;
    flex-flow: column nowrap;
    margin-left: 0.75rem;
    justify-content: flex-start;
    width: 100%;

    & > * {
      width: 100%;
      margin: 1rem 0 0;

      &:first-child {
        margin-top: 0;
      }
    }

    & > img {
      width: 100%;
      height: auto;

      @media (max-width: ${style.collapse}px) {
        border-radius: ${style.borderRadius};
      }
    }

    h4,
    p {
      line-height: 1.5;
      font-size: 1rem;
    }

    h4 + div,
    p + p {
      margin-top: 0.5rem;
    }

    p {
      margin: 0;
    }

    ${Button} {
      justify-content: center;
      align-self: flex-start;
      width: auto;
      max-width: 100;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
`;

const AnnouncementCard = (props) => {
  const { image, title, content, link, linkLabel, config } = props;

  return (
    <StyledCard>
      <FeatherIcon name={config.icon} color={style.black500} />
      <article>
        {image?.activity && <img src={image.activity} />}
        <h4>{title}</h4>
        <div dangerouslySetInnerHTML={{ __html: content }} />
        {link && (
          <Button as="a" href={link} color="primary" small>
            {linkLabel || "En savoir plus"}
          </Button>
        )}
      </article>
    </StyledCard>
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
};
export default AnnouncementCard;
