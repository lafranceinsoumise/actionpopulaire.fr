import PropTypes from "prop-types";
import React from "react";
import { useLocation } from "react-router-dom";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledWrapper = styled.div`
  display: flex;
  width: 100%;
  flex-flow: column nowrap;
  gap: 0.5rem;

  ${Button} {
    ${"" /* TODO: remove after Button refactoring merge */}
    width: 100%;
    margin: 0;
    justify-content: center;
  }

  p {
    margin: 0.5rem 0 0;
    text-align: center;
    font-size: 0.688rem;
    font-weight: 400;
    line-height: 1.5;
    color: ${(props) => props.theme.text700};
  }
`;

const AnonymousActions = ({ isOpen }) => {
  const location = useLocation();
  return (
    <StyledWrapper>
      <Button
        $block
        link
        color="success"
        route="login"
        disabled={!isOpen}
        title={
          isOpen
            ? "Rejoindre le groupe"
            : "Il n'est pas possible de rejoindre ce groupe"
        }
        state={{
          from: "group",
          next: location.pathname,
        }}
        icon="plus"
      >
        Rejoindre
      </Button>
      {isOpen && (
        <Button
          $block
          link
          route="login"
          state={{
            from: "group",
            next: location.pathname,
          }}
          icon="rss"
        >
          Suivre
        </Button>
      )}
    </StyledWrapper>
  );
};
AnonymousActions.propTypes = {
  isOpen: PropTypes.bool,
};
export default AnonymousActions;
