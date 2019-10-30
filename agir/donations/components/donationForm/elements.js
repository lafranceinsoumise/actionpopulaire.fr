import styled from "styled-components";

export const FlexContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  justify-content: ${({ justifyContent }) => justifyContent || "space-between"};
  margin-bottom: 15px;
`;
