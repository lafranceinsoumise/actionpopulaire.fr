import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import DownloadApp from "@agir/front/genericComponents/DownloadApp";
import NavBar from "./NavBar";

const StyledPageHead = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  z-index: ${(props) => props.theme.zindexTopBar};
  width: 100%;
  background-color: ${(props) => props.theme.white};
  isolation: isolate;
`;

const TopBar = ({ path, hideBannerDownload }) => {
  return (
    <StyledPageHead>
      {!hideBannerDownload && <DownloadApp />}
      <NavBar path={path} />
    </StyledPageHead>
  );
};

TopBar.propTypes = {
  path: PropTypes.string,
  hideBannerDownload: PropTypes.bool,
};
export default TopBar;
