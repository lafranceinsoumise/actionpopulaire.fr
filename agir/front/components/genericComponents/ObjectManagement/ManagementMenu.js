import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { NavLink } from "react-router-dom";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { Hide } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import BackButton from "./BackButton";

const StyledWarning = styled.p`
  font-size: 0.875rem;
  color: ${style.black700};
  background-color: ${style.black100};
  border-radius: 0.5rem;
  padding: 1rem;

  &:empty {
    display: none;
  }

  strong {
    font-weight: 600;
  }
`;

const StyledMenuItem = styled(NavLink)`
  display: flex;
  width: 100%;
  flex-flow: row nowrap;
  align-items: center;
  background-color: transparent;
  text-align: left;
  border: none;
  margin: 0;
  padding: 0;
  font-size: 1rem;
  line-height: 1.1;
  font-weight: 500;
  color: ${({ disabled, $cancel }) =>
    $cancel ? style.redNSP : disabled ? style.black500 : style.black1000};
  cursor: ${({ disabled }) => (disabled ? "default" : "pointer")};

  && {
    text-decoration: none;
  }

  &:hover {
    text-decoration: none;
    cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
    color: ${({ disabled, $cancel }) =>
      $cancel ? style.redNSP : disabled ? style.black500 : style.primary500};
  }

  & > * {
    margin: 0;
    padding: 0;
  }

  span {
    flex: 1 1 auto;
  }

  small {
    font-size: 0.75rem;
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: ${({ disabled, active }) => {
      if (disabled) return style.black100;
      if (active) return style.primary500;
      return style.secondary500;
    }};
    color: ${({ disabled, active }) => {
      if (disabled) return style.black500;
      if (active) return "#fff";
      return style.black1000;
    }};
    margin-right: 1rem;
    clip-path: circle(1rem);
    text-align: center;
  }

  &.active {
    span {
      color: ${({ $cancel, disabled }) =>
        $cancel ? style.redNSP : disabled ? style.black500 : style.primary500};
    }

    ${RawFeatherIcon} {
      background-color: ${({ disabled }) => {
        if (disabled) return style.black100;
        return style.primary500;
      }};
      color: ${({ disabled }) => {
        if (disabled) return style.black500;
        return style.white;
      }};
    }
  }
`;

const StyledMenu = styled.div`
  width: 100%;
  height: 100%;
  padding: 1.5rem;
  background-color: ${style.black25};
  box-shadow: inset -1px 0px 0px #dfdfdf;
  overflow: auto;

  @media (min-width: ${style.collapse}px) {
    width: 360px;
  }

  @media (max-width: ${style.collapse}px) {
    background-color: ${style.white};
  }

  h6 {
    font-size: 0.875rem;
    font-weight: 400;
    color: ${style.black700};
    margin: 0;
    padding-bottom: 0.25rem;

    &:empty {
      display: none;
    }
  }

  h4 {
    font-weight: 700;
    font-size: 1.25rem;
    line-height: 1.5;
    margin: 0;
  }

  ul {
    list-style: none;
    padding: 0 0 2rem;
    margin: 0;

    li {
      padding: 0.5rem 0;
    }

    hr {
      border-color: ${style.black200};
      margin: 0.5rem 0 1.5rem;
    }

    hr:first-child,
    li:first-child + hr,
    hr + li + hr {
      display: none;
      margin: 0;
    }
  }
`;

const ManagementMenuItem = (props) => {
  const { disabled, getLink, icon, label, disabledLabel, isCancel } = props;

  return (
    <StyledMenuItem to={getLink()} $cancel={isCancel} disabled={disabled}>
      {icon && <RawFeatherIcon width="1rem" height="1rem" name={icon} />}
      <div>
        <span>{label}</span>
        {disabled && (
          <span style={{ fontSize: "12px" }}>
            <br />
            {disabledLabel}
          </span>
        )}
      </div>
    </StyledMenuItem>
  );
};

ManagementMenuItem.propTypes = {
  id: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.func, PropTypes.string]),
  textDisabled: PropTypes.string,
  icon: PropTypes.string,
  disabled: PropTypes.bool,
  disabledLabel: PropTypes.node,
  getLink: PropTypes.func.isRequired,
  menuGroup: PropTypes.number,
  isCancel: PropTypes.bool,
};

const ManagementMenu = (props) => {
  const { items, title, subtitle, warning, onBack, children } = props;

  const groupedItems = useMemo(
    () =>
      Object.values(
        items.reduce((o, item) => {
          if (item.menuGroup) {
            o[item.menuGroup] = o[item.menuGroup] || [];
          }
          o[item.menuGroup].push(item);
          return o;
        }, {}),
      ),
    [items],
  );

  return (
    <StyledMenu id="managementMenu">
      <Hide $over>
        <BackButton onClick={onBack} />
      </Hide>
      <Spacer size="1rem" />
      <h6>{subtitle}</h6>
      <h4>{title}</h4>
      <Spacer size="0.5rem" />
      <StyledWarning>{warning}</StyledWarning>
      <Spacer size="0.5rem" />
      <ul>
        {groupedItems.map((list, i) => (
          <React.Fragment key={i}>
            {i > 0 && <hr />}
            {list.map((item) => (
              <li key={item.id}>
                <ManagementMenuItem {...item} />
              </li>
            ))}
          </React.Fragment>
        ))}
      </ul>
      {children}
    </StyledMenu>
  );
};
ManagementMenu.propTypes = {
  title: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  warning: PropTypes.node,
  items: PropTypes.arrayOf(PropTypes.shape(ManagementMenuItem.propTypes))
    .isRequired,
  onBack: PropTypes.func.isRequired,
  children: PropTypes.node,
};

export default ManagementMenu;
