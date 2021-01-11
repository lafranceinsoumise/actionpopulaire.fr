import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "@agir/front/genericComponents/Card";

import { FaFacebook, FaTwitter, FaYoutube, FaInstagram } from "react-icons/fa";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

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

  ul {
    list-style: none;
    padding: 0;
    font-size: 14px;
    font-weight: 400;
  }

  li {
    color: ${style.primary500};
    display: flex;
    align-items: baseline;

    a {
      display: inline-block;
      height: 26px;
      color: ${style.black1000};
    }
  }
`;

const LinkIcon = ({ url }) => {
  switch (true) {
    case /youtube.com/.test(url):
      return <FaYoutube style={{ color: "#ff0000" }} />;
    case /twitter.com/.test(url):
      return <FaTwitter style={{ color: "#1da1f2" }} />;
    case /facebook.com/.test(url):
      return <FaFacebook style={{ color: "#1778f2" }} />;
    case /instagram.com/.test(url):
      return <FaInstagram style={{ color: "#000000" }} />;
    default:
      return <FeatherIcon name="globe" small inline />;
  }
};
LinkIcon.propTypes = {
  url: PropTypes.string,
};

const GroupLinks = (props) => {
  const { links } = props;

  if (!Array.isArray(links)) {
    return null;
  }

  return (
    <StyledCard>
      <h4>Nos liens</h4>
      <ul>
        {links.map((link) => (
          <li key={link.url}>
            <LinkIcon url={link.url} />
            &ensp;
            <a href={link.url}>{link.name}</a>
          </li>
        ))}
      </ul>
    </StyledCard>
  );
};

GroupLinks.propTypes = {
  links: PropTypes.arrayOf(
    PropTypes.shape({
      url: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
    })
  ),
};
export default GroupLinks;
