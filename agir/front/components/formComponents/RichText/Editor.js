import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import ReactQuill from "react-quill";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import "react-quill/dist/quill.snow.css";

const StyledEditor = styled(ReactQuill)`
  z-index: 0;
  width: 100%;
  min-height: 80px;
  padding: 0;
  font-size: 1rem;
  border: 1px solid;
  border-radius: ${style.softBorderRadius};
  border-color: ${({ $invalid, $focused, readOnly }) => {
    if ($invalid) {
      return style.redNSP;
    }
    if (readOnly) {
      return style.black100;
    }
    if ($focused) {
      return style.black1000;
    }
    return style.black100;
  }};

  && > .ql-container {
    border: none;
    padding: 1rem;

    .ql-blank::before {
      font-style: normal;
      top: 0;
      left: 0;
      padding: 1rem;
    }

    .ql-editor {
      padding: 0;
      font-family: ${style.fontFamilyBase};
      font-size: 1rem;
      line-height: ${style.lineHeightBase};
      color: ${style.textColor};
      h1,
      h2,
      h3,
      h4,
      h5,
      h6 {
        font-weight: 600;
        line-height: 1.2;
        color: #00232c;
        margin-top: 0.5em;
        margin-bottom: 0.7em;
      }
      h1 {
        font-size: 2.563em;
      }
      h2 {
        font-size: 2.125em;
      }
      h3 {
        font-size: 1.125em;
      }
      h4 {
        font-size: 1.125em;
      }
      h5 {
        font-size: 1em;
      }
      h6 {
        font-size: 0.875em;
      }
      p {
        margin: 0 0 0.688em;
        a,
        a:hover,
        a:focus {
          color: inherit;
          text-decoration: underline;
        }
      }
      a {
        color: ${style.linkColor};
        text-decoration: none;
        font-weight: 600;

        &:hover,
        &:focus {
          color: ${style.linkHoverColor};
          text-decoration: ${style.linkHoverDecoration};
        }

        &:focus {
          outline: 5px auto -webkit-focus-ring-color;
          outline-offset: -2px;
        }
      }
      strong {
        font-weight: 600;
      }
    }
  }

  && > .ql-toolbar {
    border: none;
    border-bottom: 1px solid ${style.black100};

    @media (max-width: ${style.collapse}px) {
      display: ${({ $focused }) => ($focused ? "block" : "none")};
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      z-index: 1;
      border: none;
      background-color: white;
      box-shadow: 0px -3px 3px rgba(0, 35, 44, 0.1),
        0px 2px 0px rgba(0, 35, 44, 0.08);
    }

    .ql-null {
      display: none;
    }

    button {
      color: ${style.black500};

      .ql-fill {
        fill: ${style.black500};
      }
      .ql-stroke {
        stroke: ${style.black500};
      }

      &.ql-active,
      &:hover,
      &:focus {
        color: ${style.black1000};
        .ql-fill {
          fill: ${style.black1000};
        }
        .ql-stroke {
          stroke: ${style.black1000};
        }
      }
    }
  }
`;

const MODULES = {
  toolbar: [
    "null",
    { header: 1 },
    { header: 2 },
    "bold",
    "italic",
    "underline",
    "strike",
    "link",
  ],
};

const Editor = (props) => {
  const { value, onChange, disabled, hasError, ...rest } = props;
  const [isFocused, setIsFocused] = useState(false);
  const handleFocus = useCallback(() => setIsFocused(true), []);
  const handleBlur = useCallback(() => setIsFocused(false), []);

  return (
    <StyledEditor
      {...rest}
      $valid={!hasError}
      $invalid={hasError}
      $empty={!value}
      $focused={isFocused}
      value={value}
      onChange={onChange}
      readOnly={disabled}
      theme="snow"
      modules={MODULES}
      onFocus={handleFocus}
      onBlur={handleBlur}
    />
  );
};
Editor.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  hasError: PropTypes.bool,
};
export default Editor;
