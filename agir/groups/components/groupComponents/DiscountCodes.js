import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { parseDiscountCodes } from "@agir/groups/groupPage/utils";

import ShareLink from "@agir/front/genericComponents/ShareLink";

const StyledSection = styled.section`
  margin: 1.5rem 0 0;

  & > * {
    color: ${(props) => props.theme.text1000};
    margin: 0.5rem 0;
  }
`;

const StyledList = styled.ul`
  margin-bottom: 1rem;
  padding: ${(props) => (props.$special ? "1rem" : 0)};
  background-color: ${(props) =>
    props.$special ? props.theme.primary100 : "transparent"};
  border-radius: ${(props) => props.theme.borderRadius};
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;

  &:empty {
    display: none;
  }

  & > li {
    list-style: none;
    display: flex;
    flex-flow: column nowrap;
    gap: 0.25rem;

    strong {
      font-weight: 600;
    }

    span {
      font-weight: 400;
    }

    em {
      font-size: 0.875rem;
    }
  }
`;

const DiscountCode = (props) => {
  const { dateExact, code, label } = props;

  return (
    <li key={code}>
      {label && <strong>🎟️&nbsp;{label}</strong>}
      <ShareLink color="secondary" url={code} label="Copier" $wrap={400} />
      <em>Valable jusqu'au {dateExact}</em>
    </li>
  );
};

DiscountCode.propTypes = {
  dateExact: PropTypes.string,
  code: PropTypes.string,
  label: PropTypes.string,
};

const DiscountCodes = ({ discountCodes, ...rest }) => {
  const [codes, specialCodes] = useMemo(
    () => parseDiscountCodes(discountCodes),
    [discountCodes],
  );

  if (!Array.isArray(codes) || codes.length === 0) {
    return null;
  }

  return (
    <StyledSection {...rest}>
      <h5>Codes matériels</h5>
      {specialCodes.length > 0 && (
        <StyledList $special>
          {specialCodes.map((data) => (
            <DiscountCode key={data.code} {...data} />
          ))}
        </StyledList>
      )}
      <StyledList>
        {codes.map((data) => (
          <DiscountCode key={data.code} {...data} />
        ))}
      </StyledList>
    </StyledSection>
  );
};

DiscountCodes.propTypes = {
  discountCodes: PropTypes.array,
};

export default DiscountCodes;
