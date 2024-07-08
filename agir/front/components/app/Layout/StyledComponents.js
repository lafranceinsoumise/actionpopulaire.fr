import styled from "styled-components";

export const LayoutSubtitle = styled.h2`
  color: ${(props) => props.theme.text700};
  font-weight: 400;
  font-size: 0.875rem;
  margin: 0.75rem 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;

export const LayoutTitle = styled.h1`
  display: flex;
  align-items: center;
  font-size: 1.625rem;
  margin: 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;
