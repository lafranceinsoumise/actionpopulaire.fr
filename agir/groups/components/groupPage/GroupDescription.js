import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";
import Collapsible from "@agir/front/genericComponents/Collapsible";

const StyledCard = styled(Card)`
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;

  & > * {
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }
  h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }
`;

const GroupDescription = (props) => {
  const { description } = props;

  if (!description || !String(description).trim()) {
    return null;
  }

  return (
    <StyledCard>
      <h4>Présentation</h4>
      <Collapsible
        dangerouslySetInnerHTML={{ __html: description.trim() }}
        expanderLabel="Lire la suite"
        maxHeight={92}
        fadingOverflow
      />
    </StyledCard>
  );
};

GroupDescription.propTypes = {
  description: PropTypes.string,
};
export default GroupDescription;
