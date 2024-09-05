import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

import Link from "@agir/front/app/Link";

const SettingsMenuLink = styled(Link)`
  position: absolute;
  padding: 6px 5px;
  bottom: 0;
  right: 0;
  background-color: ${(props) => props.theme.text1000};
  color: ${(props) => props.theme.text25};
  width: 42px;
  height: 42px;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  transform: translateY(100%);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 0 0);
  transition: all 100ms ease-in-out;
  cursor: pointer;
  opacity: 0.75;

  &:hover,
  &:focus {
    background-color: ${(props) => props.theme.text1000};
    color: ${(props) => props.theme.background0};
    opacity: 1;
  }
`;

const AdminLink = ({ link }) =>
  link ? (
    <SettingsMenuLink
      to={link.to}
      href={link.href}
      route={link.route}
      title={link.label}
      aria-label={link.label}
      className="small-only"
    >
      <FeatherIcon name="settings" />
    </SettingsMenuLink>
  ) : null;

AdminLink.propTypes = {
  link: PropTypes.shape({
    to: PropTypes.string,
    href: PropTypes.string,
    route: PropTypes.string,
    label: PropTypes.string,
  }),
};
export default AdminLink;
