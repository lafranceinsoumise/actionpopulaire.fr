/* eslint react/display-name: "off" */

import PropTypes from "prop-types";
import React, { useMemo } from "react";
import regexifyString from "regexify-string";
import styled from "styled-components";

const StyledContent = styled.p`
  & > span {
    display: block;
    min-height: 1em;
    font-size: inherit;
    line-height: inherit;
  }
`;

const URL_RE = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/gi;

const parseString = (input) =>
  regexifyString({
    pattern: URL_RE,
    decorator: (match, index) => (
      <a
        target="_blank"
        rel="noopener noreferrer"
        key={match + index}
        href={match}
      >
        {match}
      </a>
    ),
    input,
  });

const ParsedString = ({ children, ...rest }) => {
  const spans = useMemo(() => {
    if (typeof children !== "string") {
      return null;
    }
    const spans = children
      .split("\n")
      .map((paragraph, i) => (
        <span key={i + "__" + paragraph}>{parseString(paragraph)}</span>
      ));
    return spans;
  }, [children]);

  return spans ? <StyledContent {...rest}>{spans}</StyledContent> : children;
};
ParsedString.propTypes = {
  children: PropTypes.string.isRequired,
};
export default ParsedString;
