import React, { useEffect, useRef } from "react";
import styled, { useTheme } from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledWrapper = styled.div`
  padding: 1rem 0;
  text-align: center;

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    margin: 0;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.25rem;
    }
  }

  strong {
    font-weight: 600;
  }
`;

const FormSuccess = ({ children }) => {
  const topRef = useRef();
  const theme = useTheme();

  useEffect(() => {
    topRef.current && topRef.current.scrollIntoView(true);
  }, []);

  return (
    <StyledWrapper ref={topRef}>
      <svg
        width="64"
        height="64"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M33.3333 61.3333C50.27 61.3333 64 47.6034 64 30.6667C64 13.7299 50.27 0 33.3333 0C16.3966 0 2.66663 13.7299 2.66663 30.6667C2.66663 47.6034 16.3966 61.3333 33.3333 61.3333ZM47.0737 25.7948C48.0649 24.8336 48.0892 23.2508 47.128 22.2596C46.1669 21.2684 44.5841 21.2441 43.5929 22.2052L28.8333 36.5176L23.0737 30.9325C22.0824 29.9713 20.4997 29.9957 19.5385 30.9869C18.5774 31.9781 18.6017 33.5608 19.5929 34.522L27.0929 41.7948C28.0626 42.7351 29.6039 42.7351 30.5737 41.7948L47.0737 25.7948Z"
          fill={theme.success500}
        />
      </svg>
      <Spacer size="0.875rem" />
      {children}
      <Spacer size="1.5rem" />
      <footer>
        <Button color="dismiss" icon="arrow-right" link route="legislative2024">
          Retourner sur le site
        </Button>
      </footer>
    </StyledWrapper>
  );
};

export default FormSuccess;
