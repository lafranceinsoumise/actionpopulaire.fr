import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledCard = styled(Card)`
  display: flex;
  flex-flow: column nowrap;
  align-items: flex-start;
  gap: 0.5rem;

  & > * {
    flex: 0 0 auto;
    margin: 0;
  }

  & > h5 {
    display: flex;
    flex-flow: row nowrap;
    gap: 0.5rem;
    align-items: flex-start;
    line-height: 1.5;
    min-height: 1px;
    max-width: 100%;

    & > ${RawFeatherIcon} {
      flex: 0 0 auto;
    }

    & > span {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }

  & > p {
    font-size: 0.875rem;
    color: ${style.black700};
    margin-bottom: 0.25rem;
  }
`;

const FileCard = (props) => {
  const { title, text, icon, downloadLabel, downloadIcon, route } = props;

  return (
    <StyledCard>
      <h5>
        <RawFeatherIcon name={icon || "file-text"} small />
        <span>{title}</span>
      </h5>
      <p>{text}</p>
      <Button
        link
        small
        route={route}
        color="primary"
        icon={downloadIcon || "download"}
      >
        {downloadLabel || "Télécharger le document"}
      </Button>
    </StyledCard>
  );
};
FileCard.propTypes = {
  title: PropTypes.node.isRequired,
  text: PropTypes.node.isRequired,
  icon: PropTypes.string,
  route: PropTypes.string.isRequired,
  downloadLabel: PropTypes.node,
  downloadIcon: PropTypes.string,
};
export default FileCard;
