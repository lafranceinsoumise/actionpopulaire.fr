import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

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

    & > strong {
      font-size: 0.75rem;
      color: ${style.primary600};
      background-color: ${style.primary100};
      padding: 0.25rem 0.5rem;
      border-radius: 0.5rem;

      @media (max-width: ${style.collapse}px) {
        display: none;
      }
    }
  }

  & > p {
    font-size: 0.875rem;
    color: ${style.black700};
    margin-bottom: 0.25rem;
  }
`;

const FileCard = (props) => {
  const { title, text, icon, downloadLabel, downloadIcon, route, href, isNew } =
    props;

  const isDesktop = useIsDesktop();

  return (
    <StyledCard>
      <h5>
        <RawFeatherIcon name={icon || "file-text"} />
        {isNew && <strong>Nouveau</strong>}
        <span>{title}</span>
      </h5>
      <p>{text}</p>
      <Button
        block={!isDesktop}
        link
        small
        route={route}
        href={href}
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
  route: PropTypes.string,
  href: PropTypes.string,
  downloadLabel: PropTypes.node,
  downloadIcon: PropTypes.string,
  isNew: PropTypes.bool,
};
export default FileCard;
