import React from "react";
import styled from "styled-components";

import {
  FlexContainer,
  MarginBox,
} from "@agir/donations/donationForm/elements";

export const AllocationsArray = styled(MarginBox)`
  display: table;
  width: 100%;
  margin: 30px auto 0;
  max-width: 500px;
`;

export const Row = (props) => (
  <FlexContainer $alignItems="center" {...props} s />
);

export const RecipientLabel = styled.div`
  text-align: left;
`;

export const RecipientContainer = styled.div`
  flex: 0 0 100%;
  font-weight: bold;
  width: 25rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
  }
`;

export const ButtonHolder = styled(MarginBox)`
  text-align: center;
`;

export const AlignedButton = styled.button`
  width: 3rem;
  font-size: 2rem;
  color: #9f3723;
  border: none;
  background: none;
`;

export const SliderContainer = styled.div`
  flex-grow: 1;
  margin: 0 1.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;

export const AmountBoxContainer = styled.div`
  max-width: 12rem;
  margin: 10px 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: 100%;
  }

  & .input-group {
    z-index: 0;
  }
`;
