import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import Card from "./GroupPageCard";
import LinkIcon from "@agir/front/genericComponents/LinkIcon";

const StyledList = styled.ul`
  list-style: none;
  padding: 0;
  font-size: 14px;
  font-weight: 400;

  li {
    color: ${style.primary500};
    display: flex;
    height: 27px;
    align-items: center;

    a {
      max-width: 240px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      display: inline-block;
      color: ${style.black1000};
    }
  }
`;

const GroupLinks = (props) => {
  const { links, editLinkTo } = props;

  if (!Array.isArray(links) || links.length === 0) {
    return null;
  }

  return (
    <Card title="Nos liens" editLinkTo={editLinkTo}>
      <StyledList>
        {links.map((link) => (
          <li title={link.label} key={link.id}>
            <LinkIcon url={link.url} />
            &ensp;
            <a href={link.url} target="_blank" rel="noopener noreferrer">
              {link.label}
            </a>
          </li>
        ))}
      </StyledList>
    </Card>
  );
};

GroupLinks.propTypes = {
  links: PropTypes.arrayOf(
    PropTypes.shape({
      url: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    }),
  ),
  editLinkTo: PropTypes.string,
};
export default GroupLinks;
