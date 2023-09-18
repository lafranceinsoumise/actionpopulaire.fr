import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import ReactQuill, { Quill } from "react-quill";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import "react-quill/dist/quill.snow.css";

const QuillIcons = Quill.import("ui/icons");

QuillIcons.header["3"] = `
<svg width="17px" height="12px" viewBox="0 0 17 12" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g id="Page-1" stroke="none" strokeWidth="1" fill="none" fill-rule="evenodd">
        <g id="h3" fill="currentColor">
            <path d="M1.992,12.728 C1.81066576,12.9093342 1.58966797,13 1.329,13 C1.06833203,13 0.84733424,12.9093342 0.666,12.728 C0.48466576,12.5466658 0.394,12.325668 0.394,12.065 L0.394,1.525 C0.394,1.26433203 0.48466576,1.04333424 0.666,0.862 C0.84733424,0.68066576 1.06833203,0.59 1.329,0.59 C1.58966797,0.59 1.81066576,0.68066576 1.992,0.862 C2.17333424,1.04333424 2.264,1.26433203 2.264,1.525 L2.264,5.503 C2.264,5.60500051 2.31499949,5.656 2.417,5.656 L7.381,5.656 C7.48300051,5.656 7.534,5.60500051 7.534,5.503 L7.534,1.525 C7.534,1.26433203 7.62466576,1.04333424 7.806,0.862 C7.98733424,0.68066576 8.20833203,0.59 8.469,0.59 C8.72966797,0.59 8.95066576,0.68066576 9.132,0.862 C9.31333424,1.04333424 9.404,1.26433203 9.404,1.525 L9.404,12.065 C9.404,12.325668 9.31333424,12.5466658 9.132,12.728 C8.95066576,12.9093342 8.72966797,13 8.469,13 C8.20833203,13 7.98733424,12.9093342 7.806,12.728 C7.62466576,12.5466658 7.534,12.325668 7.534,12.065 L7.534,7.271 C7.534,7.16899949 7.48300051,7.118 7.381,7.118 L2.417,7.118 C2.31499949,7.118 2.264,7.16899949 2.264,7.271 L2.264,12.065 C2.264,12.325668 2.17333424,12.5466658 1.992,12.728 Z M11.32,7.07 C11.1666659,7.07 11.0333339,7.0133339 10.92,6.9 C10.8066661,6.7866661 10.75,6.6533341 10.75,6.5 L10.75,6.27 C10.75,6.1166659 10.8066661,5.9833339 10.92,5.87 C11.0333339,5.7566661 11.1666659,5.7 11.32,5.7 L15.05,5.7 C15.2033341,5.7 15.3366661,5.7566661 15.45,5.87 C15.5633339,5.9833339 15.62,6.1166659 15.62,6.27 L15.62,6.5 C15.62,6.8800019 15.4733348,7.1899988 15.18,7.43 L13.67,8.68 L13.67,8.69 C13.67,8.6966667 13.6733333,8.7 13.68,8.7 L13.8,8.7 C14.3800029,8.7 14.8449983,8.8799982 15.195,9.24 C15.5450018,9.6000018 15.72,10.0866636 15.72,10.7 C15.72,11.4733372 15.4833357,12.0666646 15.01,12.48 C14.5366643,12.8933354 13.8566711,13.1 12.97,13.1 C12.436664,13.1 11.8966694,13.0366673 11.35,12.91 C11.1899992,12.8699998 11.0583339,12.7816674 10.955,12.645 C10.8516662,12.5083327 10.8,12.3533342 10.8,12.18 L10.8,11.84 C10.8,11.706666 10.8549995,11.6016671 10.965,11.525 C11.0750006,11.448333 11.196666,11.4299998 11.33,11.47 C11.9033362,11.6566676 12.4033312,11.75 12.83,11.75 C13.2166686,11.75 13.5166656,11.6600009 13.73,11.48 C13.9433344,11.2999991 14.05,11.0500016 14.05,10.73 C14.05,10.4033317 13.9266679,10.173334 13.68,10.04 C13.4333321,9.906666 12.9733367,9.8366667 12.3,9.83 C12.1466659,9.83 12.0133339,9.77500055 11.9,9.665 C11.7866661,9.55499945 11.73,9.4233341 11.73,9.27 L11.73,9.25 C11.73,8.8766648 11.8733319,8.5666679 12.16,8.32 L13.58,7.09 L13.58,7.08 C13.58,7.0733333 13.5766667,7.07 13.57,7.07 L11.32,7.07 Z" id="Shape" fill-rule="nonzero"></path>
        </g>
    </g>
</svg>`;

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
      return style.black500;
    }
    return style.black100;
  }};
  background-color: ${({ readOnly }) =>
    readOnly ? style.black100 : "transparent"};

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
      color: ${({ readOnly }) => (readOnly ? style.black500 : style.textColor)};
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
      box-shadow:
        0px -3px 3px rgba(0, 35, 44, 0.1),
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
    { header: 2 },
    { header: 3 },
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
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);
  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

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
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  hasError: PropTypes.bool,
};
export default Editor;
