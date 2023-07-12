/* eslint react/display-name: "off" */

import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

const StyledContent = styled.p`
  & > span {
    display: block;
    min-height: 1em;
    font-size: inherit;
    line-height: inherit;
  }
`;

const URL_RE =
  /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/gi;

const replaceSubstrings = (options) => {
  const { pattern, formatter, input } = options;
  const output = [];
  let matchIndex = 0;
  let processedInput = input;
  let result = pattern.exec(processedInput);
  while (result !== null) {
    const matchStartAt = result.index;
    const match = result[0];
    const contentBeforeMatch = processedInput.substring(0, matchStartAt);
    const decoratedMatch = formatter(match, matchIndex);
    output.push(contentBeforeMatch);
    output.push(decoratedMatch);
    processedInput = processedInput.substring(
      matchStartAt + match.length,
      processedInput.length + 1,
    );
    pattern.lastIndex = 0;
    result = pattern.exec(processedInput);
    matchIndex += 1;
  }
  if (processedInput) {
    output.push(processedInput);
  }

  return output;
};

const parseString = (input) =>
  replaceSubstrings({
    pattern: URL_RE,
    formatter: (match, index) => (
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
