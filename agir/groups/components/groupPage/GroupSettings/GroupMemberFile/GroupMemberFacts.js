import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

const StyledList = styled.ul`
  padding: 0;
  margin: 0;
  list-style-position: inside;

  h4 {
    font-size: 1rem;
    margin: 0;
    line-height: 1.5;
    font-weight: 600;
    padding-bottom: 0.5rem;
  }

  li::marker {
    color: ${(props) => props.theme.primary500};
  }
`;

const GroupMemberFacts = (props) => {
  const { isPoliticalSupport, isLiaison, hasGroupNotifications } = props;

  return [isPoliticalSupport, hasGroupNotifications, isLiaison].some(
    (i) => typeof i === "boolean",
  ) ? (
    <StyledList>
      <h4>À propos</h4>
      <li>
        {isPoliticalSupport
          ? "Soutien politique de la France insoumise"
          : "N’est pas encore soutien politique de la France insoumise"}
      </li>
      <li>
        {hasGroupNotifications
          ? "Est abonné·e à l’actualité de votre groupe"
          : "N'est pas abonné·e à l’actualité de votre groupe"}
      </li>
      {isLiaison && <li>Correspondant·e de son immeuble</li>}
    </StyledList>
  ) : null;
};

GroupMemberFacts.propTypes = {
  isPoliticalSupport: PropTypes.bool,
  isLiaison: PropTypes.bool,
  hasGroupNotifications: PropTypes.bool,
};

export default GroupMemberFacts;
