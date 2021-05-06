import PropTypes from "prop-types";
import React from "react";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledLink = styled.a`
  display: inline-flex;
  align-items: center;
  flex-direction: row;
  font-weight: 2rem;
  font-size: 1rem;
  color: ${style.black1000};
`;

const StyledRow = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
  justify-content: space-between;
`;

const StyledTextLink = styled.span`
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
`;

const GroupLink = (props) => {
  const { label, url, onChange } = props;

  return (
    <StyledRow>
      <StyledLink href={url} target="_blank" rel="noopener noreferrer">
        <RawFeatherIcon
          name="globe"
          width="1rem"
          height="1rem"
          style={{ color: style.primary500, marginRight: "1rem" }}
        />
        <StyledTextLink>
          {label}
          <RawFeatherIcon
            name="external-link"
            width="1rem"
            height="1rem"
            style={{ marginLeft: "0.5rem", marginRight: "0.5rem" }}
          />
        </StyledTextLink>
      </StyledLink>

      <RawFeatherIcon
        name="edit-2"
        width="1rem"
        height="1rem"
        style={{ cursor: "pointer" }}
        onClick={onChange}
      />
    </StyledRow>
  );
};
GroupLink.propTypes = {
  label: PropTypes.string,
  url: PropTypes.string,
  onChange: PropTypes.func,
};
export default GroupLink;
