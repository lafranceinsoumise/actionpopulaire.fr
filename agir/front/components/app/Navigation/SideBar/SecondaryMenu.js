import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";

const StyledLink = styled(Link)``;

const StyledMenu = styled.ul`
  width: 100%;
  margin-top: 0;
  margin-bottom: 1rem;
  list-style-type: none;
  font-weight: 400;
  color: ${(props) => props.theme.black500};

  h6 {
    font-size: 12px;
    line-height: 15px;
    color: ${(props) => props.theme.black500};
    margin-bottom: 0.5rem;
    font-weight: bold;
    overflow-wrap: break-word;
  }

  li {
    display: block;
    line-height: 1.2;
    margin: 0 0 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    max-width: 100%;
    text-overflow: ellipsis;

    ${StyledLink} {
      &,
      &:hover,
      &:focus,
      &:active {
        color: ${(props) => props.theme.black700};
        font-weight: 400;
        font-size: 13px;
        line-height: inherit;
      }
    }
  }
`;

const SecondaryMenu = ({ title, links, ...rest }) =>
  Array.isArray(links) && links.length > 0 ? (
    <StyledMenu {...rest}>
      {title ? <h6>{title}</h6> : null}
      {links.map((link) => (
        <li key={link.id}>
          <StyledLink
            href={link.href || undefined}
            route={link.route || undefined}
            to={link.to || undefined}
            title={link.title || link.label}
          >
            {link.title || link.label}
          </StyledLink>
        </li>
      ))}
    </StyledMenu>
  ) : null;

SecondaryMenu.propTypes = {
  title: PropTypes.string,
  links: PropTypes.arrayOf(
    PropTypes.shape({
      href: PropTypes.string,
      route: PropTypes.string,
      to: PropTypes.string,
      title: PropTypes.string,
      label: PropTypes.string,
    }),
  ),
};

export default SecondaryMenu;
