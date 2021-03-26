import React from "react";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const StyledToast = styled.div`
  padding: 1rem;
  border: 1px solid #000a2c;
  position: relative;
  margin-top: 2rem;

  div {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 6px;
    background-color: ${style.redNSP};
  }
`;

const Toast = ({ children }) => {
  return (
    <StyledToast>
      <div></div>
      {children}
    </StyledToast>
  );
};

export default Toast;
