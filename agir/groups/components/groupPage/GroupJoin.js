import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";

const StyledContent = styled.div`
  padding: 0;
  display: flex;
  align-items: flex-start;
  flex-flow: column nowrap;

  @media (max-width: ${style.collapse}px) {
    background-color: white;
    width: 100%;
    padding: 0 1rem;
    align-items: stretch;
  }

  ${Button} {
    justify-content: center;
  }

  p {
    font-weight: 500;
    font-size: 0.813rem;
    line-height: 1.5;
    color: ${style.black500};
    margin-top: 1em;

    @media (max-width: ${style.collapse}px) {
      font-size: 0.688rem;
      font-weight: 400;
      color: ${style.black1000};
    }
  }
`;

const GroupLinks = (props) => {
  const { url, is2022 = false } = props;

  if (!url) {
    return null;
  }

  return (
    <StyledContent>
      <CSRFProtectedForm method="post" action={url}>
        <input type="hidden" name="action" value="join" />
        <Button type="submit" color="primary">
          Rejoindre {is2022 ? "l'équipe" : "le groupe"}
        </Button>
      </CSRFProtectedForm>
      <p>Votre email sera communiquée aux animateur-ices</p>
    </StyledContent>
  );
};

GroupLinks.propTypes = {
  url: PropTypes.string,
  is2022: PropTypes.bool,
};
export default GroupLinks;
