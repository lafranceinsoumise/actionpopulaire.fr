import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import ShareLink from "@agir/front/genericComponents/ShareLink";

const StyledDiscountCode = styled.div`
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: ${style.cardShadow};

  & > * {
    margin: 0;
    padding: 0;
  }

  & > h5 {
    font-weight: 700;
    font-size: 16px;
    line-height: 1.5;
    padding-bottom: 0.5rem;

    span {
      text-transform: capitalize;
    }
  }

  & > div {
    max-width: 360px;
  }

  & > p {
    padding-top: 0.75rem;
    color: ${style.black700};
    font-size: 0.875rem;
    line-height: 1.5;
  }
`;

const DiscountCode = ({ code, expirationDate }) => {
  const [date, month] = useMemo(() => {
    try {
      let date = new Date(expirationDate);
      date = DateTime.fromJSDate(date).setLocale("fr");
      if (date.isValid) {
        date = date.toFormat("dd LLLL yyyy");
        return [date, date.split(" ")[1]];
      }
      return [expirationDate];
    } catch (e) {
      return [expirationDate];
    }
  }, [expirationDate]);

  return (
    <StyledDiscountCode>
      <h5>
        Code promo matériel{" "}
        {month && (
          <>
            du mois de <span>{month}</span>
          </>
        )}
      </h5>
      <ShareLink color="secondary" url={code} label="Copier" />
      <p>Expiration&nbsp;: {date}</p>
    </StyledDiscountCode>
  );
};

DiscountCode.propTypes = {
  code: PropTypes.string.isRequired,
  expirationDate: PropTypes.string.isRequired,
};
export default DiscountCode;
