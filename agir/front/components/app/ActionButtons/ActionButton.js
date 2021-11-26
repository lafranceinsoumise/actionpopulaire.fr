import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledButton = styled(Link)`
  display: inline-flex;
  flex-flow: column nowrap;
  align-items: center;
  gap: 8px;
  width: 75px;
  font-size: 12px;
  line-height: 1.5;
  font-weight: 400;
  text-align: center;
  color: ${(props) => props.theme.black700};

  @media (min-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
    flex-flow: row nowrap;
    gap: 0;
    font-size: 0.875rem;
    height: 2rem;
  }

  &,
  &:hover,
  &:focus {
    text-decoration: none;
  }

  & > span {
    flex: 0 0 50px;
    width: 50px;
    height: 50px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 100%;
    color: white;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      transform-origin: left center;
      transform: scale(0.64);
      margin-right: -10px;
    }
  }

  & > strong {
    font-weight: inherit;
    white-space: nowrap;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;

const ActionButton = (props) => {
  const { route, label, icon, color, className } = props;
  return (
    <StyledButton className={className} route={route}>
      {typeof icon === "string" ? (
        <RawFeatherIcon
          css={`
            background-color: ${color};
          `}
          name={icon}
        />
      ) : (
        icon
      )}
      {Array.isArray(label) ? (
        <strong>
          <Hide as="span" title={label[1]} over>
            {label[0]}
          </Hide>
          <Hide as="span" title={label[1]} under>
            {label[1]}
          </Hide>
        </strong>
      ) : (
        <strong title={label}>{label}</strong>
      )}
    </StyledButton>
  );
};
ActionButton.propTypes = {
  route: PropTypes.string,
  label: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
  icon: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  color: PropTypes.string,
  className: PropTypes.string,
};
export default ActionButton;
