import PropTypes from "prop-types";
import React, { useCallback, useRef, useState } from "react";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { Column, Row } from "@agir/front/genericComponents/grid";

const StyledInput = styled.input`
  min-width: 240px;
  width: 100%;
  height: 2rem;
  border: 1px solid ${style.black100};
  border-radius: 0.5rem;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
`;

const StyledDiv = styled.div`
  font-weight: 500;
`;

const ShareLink = (props) => {
  const { url, title, label, color } = props;

  let [copied, setCopied] = useState(false);
  let copyUrl = useCallback(() => {
    inputEl.current.select();
    document.execCommand("copy");
    setCopied(true);
  }, []);

  const inputEl = useRef(null);
  return (
    <StyledDiv>
      <Row gutter={2} style={{ marginBottom: "1rem" }}>
        <Column grow collapse={false}>
          {title}
        </Column>
      </Row>

      <Row gutter={4}>
        <Column grow collapse={false}>
          {" "}
          <StyledInput
            type="text"
            value={url}
            readOnly
            ref={inputEl}
            onClick={copyUrl}
          />
        </Column>
        <Column collapse={false}>
          <Button
            color={color}
            small
            icon={copied ? "check" : "copy"}
            onClick={copyUrl}
          >
            {label}
          </Button>
        </Column>
      </Row>
    </StyledDiv>
  );
};
ShareLink.propTypes = {
  title: PropTypes.string,
  url: PropTypes.string,
};
export default ShareLink;
