import PropTypes from "prop-types";
import React, { useCallback, useRef, useState } from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { Column, Row } from "@agir/front/genericComponents/grid";

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
    <Card style={{ padding: "1.5rem" }}>
      <Row gutter={2} style={{ marginBottom: "1rem" }}>
        <Column grow collapse={false}>
          {title}
        </Column>
      </Row>

      <Row gutter={4}>
        <Column grow collapse={false}>
          {" "}
          <input
            type="text"
            value={url}
            style={{
              width: "100%",
              height: "32px",
              border: `1px solid ${style.black100}`,
              borderRadius: "8px",
              padding: "8px",
            }}
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
    </Card>
  );
};
ShareLink.propTypes = {
  title: PropTypes.string,
  url: PropTypes.string,
};
export default ShareLink;
