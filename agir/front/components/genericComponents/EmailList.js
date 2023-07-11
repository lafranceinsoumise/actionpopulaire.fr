import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";

const StyledEmailList = styled.div`
  width: 100%;
  display: grid;
  grid-template-columns: 1fr auto;
  grid-gap: 0.5rem;

  @media (max-width: ${style.collapse}px) {
    grid-template-columns: 1fr;
  }

  input,
  ${Button} {
    &,
    &:hover,
    &:focus {
      height: 2rem;
      margin: 0;
      outline: none;
      border-radius: ${style.softBorderRadius};
      white-space: nowrap;
    }
  }

  input {
    display: block;
    font-size: 0.813rem;
    color: ${style.black700};
    border: 1px solid ${style.black100};
    background-color: ${style.white};
    padding: 0.25rem 0.5rem;
    cursor: text;
  }
`;

const EmailList = (props) => {
  const { data, label, ...rest } = props;
  const emails = useMemo(() => {
    if (!Array.isArray(data)) {
      return "";
    }
    return data
      .map((item) => (typeof item === "string" ? item : item.email))
      .filter(Boolean)
      .join(", ");
  }, [data]);

  const [isCopied, copy] = useCopyToClipboard(emails);

  return (
    <StyledEmailList {...rest}>
      <input type="text" value={emails} readOnly />
      <Button
        onClick={copy}
        color={isCopied ? "confirmed" : "primary"}
        icon={isCopied ? "check" : "copy"}
        small
      >
        {isCopied ? "Copié !" : label || "Copier les adresses"}
      </Button>
    </StyledEmailList>
  );
};
EmailList.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
  ),
  label: PropTypes.string,
};

export default EmailList;
