import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "./GroupPageCard";
import Collapsible from "@agir/front/genericComponents/Collapsible";

const StyledCard = styled(Card)`
  p {
    margin: 0;
  }

  p + p {
    margin-top: 11px;
  }

  && a {
    color: ${style.primary500};
    text-decoration: none;
    cursor: pointer;
    font-weight: inherit;

    &:hover {
      text-decoration: underline;
    }
  }
`;

const GroupDescription = (props) => {
  const { description, maxHeight = 92, routes, outlined } = props;

  if (!description || !String(description).trim()) {
    return null;
  }

  return (
    <StyledCard
      title="Présentation"
      editUrl={routes && routes.edit}
      outlined={outlined}
    >
      <Collapsible
        dangerouslySetInnerHTML={{ __html: description.trim() }}
        expanderLabel="Lire la suite"
        maxHeight={maxHeight}
        fadingOverflow
      />
    </StyledCard>
  );
};

GroupDescription.propTypes = {
  description: PropTypes.string,
  maxHeight: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  routes: PropTypes.object,
  outlined: PropTypes.bool,
};
export default GroupDescription;
