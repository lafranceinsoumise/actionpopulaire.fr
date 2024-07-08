import onDOMReady from "@agir/lib/utils/onDOMReady";
import PropTypes from "prop-types";
import { renderReactComponent } from "@agir/lib/utils/react";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import EmojiPicker from "@agir/front/formComponents/EmojiPicker";
import ThemeProvider, { getTheme } from "@agir/front/theme/ThemeProvider";

const StyledField = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;

  * > {
    flex: 0 0 auto;
  }

  & > input {
    max-width: 1.5rem;
    text-align: center;
    font-size: 1rem;
  }

  & > span {
    font-size: 11px;
    color: var(--body-quiet-color);
  }
`;

const EmojiField = (props) => {
  const [text, setText] = useState(props.text);
  const [value, setValue] = useState(props.value);

  const handleChange = useCallback((e) => {
    setText("");
    setValue(e.target.value);
  }, []);

  const handleSelect = useCallback((emoji) => {
    setText("");
    setValue(emoji);
  }, []);

  return (
    <StyledField>
      <EmojiPicker onSelect={handleSelect} />
      <input
        {...props}
        type="text"
        onChange={handleChange}
        onInput={handleChange}
        value={value}
      />
      <span>{text}</span>
    </StyledField>
  );
};

EmojiField.propTypes = {
  value: PropTypes.string,
  text: PropTypes.string,
};

const renderField = (originalField) => {
  const parent = originalField.parentNode;
  const renderingNode = document.createElement("div");

  renderReactComponent(
    <ThemeProvider theme={getTheme("light")}>
      <EmojiField
        {...originalField.dataset}
        value={originalField.value}
        id={originalField.id}
        name={originalField.name}
        disabled={originalField.disabled}
        minLength={originalField.minLength}
        maxLength={originalField.maxLength}
        readOnly={originalField.readOnly}
        className={originalField.className}
      />
    </ThemeProvider>,
    renderingNode,
  );

  parent.classList.remove("progress");
  originalField.replaceWith(renderingNode);
};

onDOMReady(() => {
  document
    .querySelectorAll('input[data-component="EmojiField"]')
    .forEach(renderField);
});
