import PropTypes from "prop-types";
import React, { useRef } from "react";

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
  }

  h4:empty {
    display: none;
  }

  ${StyledInput} {
    flex: 1 1 240px;
    width: 100%;
    border: 1px solid ${style.black100};
    border-radius: 0;
    padding: 0.5rem;
    margin-right: 0.5rem;

    &:hover,
    &:focus {
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
  const { url, title, label, color } = props;

  const [isCopied, handleCopy] = useCopyToClipboard(url);

  return (
    <StyledDiv>
      <h4>{title}</h4>
      <div>
        <StyledInput
          type="text"
          value={url}
          readOnly
          onClick={handleCopy}
          onFocus={handleCopy}
        />
        <Button
          small
          color={color}
          icon={isCopied ? "check" : "copy"}
          onClick={handleCopy}
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
