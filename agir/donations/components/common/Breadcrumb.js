import PropTypes from "prop-types";
import React from "react";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledBreadcrumb = styled.div`
  display: flex;
  align-items: center;
  margin-top: 1rem;

  @media (max-width: ${style.collapse}px) {
    font-size: 11px;
    span {
      margin: 2px;
      height: 11px;
      width: 11px;
    }
  }

  > div {
    cursor: pointer;
    color: ${(props) => props.theme.secondary500};
    font-weight: bold;
  }
  > div:nth-of-type(2) {
    color: ${(props) => props.theme.primary500};
  }
`;

const Breadcrumb = ({ onClick }) => (
  <StyledBreadcrumb>
    <div onClick={onClick}>1. Montant</div>
    <RawFeatherIcon name="chevron-right" width="1rem" height="1rem" />
    <div>2. Mes informations</div>
    <RawFeatherIcon name="chevron-right" width="1rem" height="1rem" />
    <div>3. Paiement</div>
  </StyledBreadcrumb>
);

Breadcrumb.propTypes = {
  onClick: PropTypes.func,
};

export default Breadcrumb;
