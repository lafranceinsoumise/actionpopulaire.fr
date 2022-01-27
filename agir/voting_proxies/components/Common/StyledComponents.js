import styled from "styled-components";

import Link from "@agir/front/app/Link";

export const StyledIllustration = styled.div``;
export const StyledBody = styled.div``;

export const StyledMain = styled.main`
  margin: 0 auto;
  padding: 0 1.5rem;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 630px;
  }

  h2 {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.5;
  }
  p {
    margin-bottom: 0;
  }
  ol {
    margin: 0;
    padding: 0;
    counter-reset: item;

    & > li {
      list-style-type: none;
      counter-increment: item;
      font-variant-numeric: tabular-nums;

      &:before {
        font-weight: 600;
        content: counter(item) ". ";
      }

      strong {
        font-weight: 600;
      }
    }
  }
  form {
    fieldset {
      margin: 0;
      padding: 0;
    }
  }
`;

export const StyledLogo = styled(Link)`
  display: block;
  width: calc(100% + 3rem);
  padding: 1rem 1.5rem;
  margin: -1rem -1.5rem 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0 -1.5rem 1rem;
    padding: 1rem;
    border-bottom: 1px solid ${(props) => props.theme.black100};
  }

  &::after {
    content: "";
    display: block;
    height: ${(props) => props.theme.logoHeight};
    background-image: url(${(props) => props.theme.logo});
    background-repeat: no-repeat;
    background-position: center center;
    background-size: contain;
  }
`;

export const StyledPage = styled.div`
  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  ${StyledIllustration} {
    flex: 0 0 524px;
    height: 100%;
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center center;
    background-image: url(${(props) => props.theme.illustration.large});

    @media (max-width: ${(props) => props.theme.collapse}px) {
      content: url(${(props) => props.theme.illustration.small});
      width: 100%;
      height: auto;
    }
  }

  ${StyledBody} {
    padding: 0 0 80px;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 auto;
      min-height: 100%;
      overflow: auto;
      padding: 80px 0;
    }
  }
`;
