import styled from "styled-components";

export const LayoutSubtitle = styled.h2`
  color: ${(props) => props.theme.black700};
  font-weight: 400;
  font-size: 14px;
  margin: 8px 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;

export const LayoutTitle = styled.h1`
  display: flex;
  align-items: center;
  font-size: 26px;
  margin: 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;
