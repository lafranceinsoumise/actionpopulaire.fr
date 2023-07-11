import PropTypes from "prop-types";
import React from "react";

import { Hide } from "@agir/front/genericComponents/grid";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";

import styled from "styled-components";

const StyledIllustration = styled.div`
  width: 100%;
  margin: 0;
  height: 10rem;
  background-repeat: no-repeat;
  background-size: contain;
  background-position: top center;
  margin-bottom: 2rem;
}
`;

const HeaderPanel = (props) => {
  const { onBack, illustration } = props;

  return (
    <>
      <Hide $over>
        <BackButton onClick={onBack} />
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
HeaderPanel.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
};
export default HeaderPanel;
