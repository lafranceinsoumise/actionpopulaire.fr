import PropTypes from "prop-types";
import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";

import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";

const StyledInput = styled.input``;

const StyledDiv = styled.div`
  font-weight: 500;

  & > div {
    height: 2rem;
    display: flex;
    flex-flow: row nowrap;
    align-items: stretch;
    max-width: 100%;
    overflow: hidden;

    ${({ $wrap }) =>
      $wrap
        ? `
      @media (max-width: ${
        typeof $wrap === "number" ? $wrap : style.collapse
      }px) {
        display: grid;
        grid-template-columns: 1fr;
        grid-gap: 0.5rem;
        height: auto;
      }
      `
        : ""}
  }

  h4:empty {
    display: none;
  }

  ${StyledInput} {
    flex: 1 1 240px;
    width: 100%;
    border: 1px solid ${style.black100};
    border-radius: ${style.softBorderRadius};
    padding: 0.5rem;
    margin-right: 0.5rem;

    &:hover:not[:disabled],
    &:focus:not[:disabled] {
      outline: none;
      border-color: ${style.black700};
    }
  }

  ${Button} {
    min-width: 0;
    flex: 0 0 auto;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;

const ShareLink = (props) => {
  const { url, title, label, color, ...rest } = props;

  const [isCopied, handleCopy] = useCopyToClipboard(url);

  return (
    <StyledDiv {...rest}>
      <h4>{title}</h4>
      <div>
        <StyledInput
          aria-label={title}
          type="text"
          value={url}
          readOnly
          disabled={!url}
        />
        <Button
          small
          color={color}
          icon={isCopied ? "check" : "copy"}
          onClick={handleCopy}
          disabled={!url}
        >
          {label || "Copier"}
        </Button>
      </div>
    </StyledDiv>
  );
};
ShareLink.propTypes = {
  title: PropTypes.string,
  url: PropTypes.string,
  label: PropTypes.string,
  color: PropTypes.string,
};
export default ShareLink;
