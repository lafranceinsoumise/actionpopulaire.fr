import styled from "styled-components";
import {
  FlexContainer,
  MarginBox
} from "@agir/donations/donationForm/elements";
import React from "react";

export const AllocationsArray = styled(MarginBox)`
  display: table;
  width: 100%;
`;

export const Row = props => <FlexContainer alignItems="center" {...props} s />;

export const RecipientLabel = styled.span`
  text-align: right;
  font-weight: bold;
  width: 25rem;
`;

export const RecipientContainer = styled.div`
  text-align: right;
  font-weight: bold;
  width: 25rem;
`;

export const ButtonHolder = styled(MarginBox)`
  text-align: right;
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
`;

export const AmountBoxContainer = styled.div`
  max-width: 12rem;
`;
