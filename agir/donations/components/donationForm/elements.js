import styled from "styled-components";

export const FlexContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  margin-bottom: 15px;

  // configurable properties
  flex-direction: ${({ $flexDirection }) => $flexDirection || "row"};
  justify-content: ${({ $justifyContent }) =>
    $justifyContent || "space-between"};
  align-items: ${({ $alignItems }) => $alignItems || "stretch"};
`;

export const MarginBox = styled.div`
  position: relative; // stacking context
  margin: ${(props) => (props.$margin ? props.$margin : "1rem 0")};
`;
