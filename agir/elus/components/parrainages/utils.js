import styled from "styled-components";

export const CadreAvertissement = styled.div`
  background-color: ${(props) => props.theme.text50};
  margin: 20px 0;
  padding: 1rem;
`;

export const MarginBlock = styled.div`
  margin: 24px 0;
`;

export const Error = styled.div`
  color: ${(props) => props.theme.error500};
  font-weight: 500;
`;
