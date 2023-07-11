import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
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

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus {
    opacity: 0.5;
    cursor: default;
    color: ${(props) => props.theme.green500};
    text-decoration: line-through;
  }

  & > ${RawFeatherIcon} {
    background-color: ${(props) => props.$color};
  }

  & > span {
    flex: 0 0 50px;
    width: 50px;
    height: 50px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 100%;
    color: ${(props) => props.$textColor || "white"};

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
  const {
    route,
    routeParams,
    label,
    icon,
    color,
    textColor,
    className,
    disabled = false,
  } = props;

  const visibileLabel = useResponsiveMemo(
    Array.isArray(label) ? label[0] : label,
    Array.isArray(label) ? label[1] : label,
  );

  return (
    <StyledButton
      $color={color}
      $textColor={textColor}
      disabled={disabled}
      onClick={disabled ? (e) => e.preventDefault() : undefined}
      onMouseDown={(e) => e.preventDefault()}
      className={className}
      route={route}
      routeParams={routeParams}
    >
      {typeof icon === "string" ? <RawFeatherIcon name={icon} /> : icon}
      <strong title={Array.isArray(label) ? label[1] : label}>
        {visibileLabel}
      </strong>
    </StyledButton>
  );
};
ActionButton.propTypes = {
  route: PropTypes.string,
  routeParams: PropTypes.object,
  label: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
  icon: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  color: PropTypes.string,
  textColor: PropTypes.string,
  className: PropTypes.string,
  disabled: PropTypes.bool,
};
export default ActionButton;
