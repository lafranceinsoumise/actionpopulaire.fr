import React from "react";

import { Hide } from "@agir/front/genericComponents/grid";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";

import styled from "styled-components";

const StyledIllustration = styled.div`
  width: 100%;
  margin: 0;
  height: 10rem;
  background-repeat: no-repeat;
  background-size: contain;
  background-position: top center;
}
`;

const HeaderPanel = (props) => {
  const { onBack, illustration } = props;

  return (
    <>
      <Hide over>
        <BackButton onBack={onBack} />
      </Hide>
      {illustration && (
        <StyledIllustration
          aria-hidden="true"
          style={{ backgroundImage: `url(${illustration})` }}
        />
      )}
    </>
  );
};

export default HeaderPanel;
