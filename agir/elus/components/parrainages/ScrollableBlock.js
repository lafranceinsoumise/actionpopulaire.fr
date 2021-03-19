import React from "react";
import styled from "styled-components";
import * as PropTypes from "prop-types";

const ScrollableBlockLayout = styled.div`
  position: relative;

  & > div {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;

    overflow-y: scroll;
  }
`;

const ScrollableBlock = ({ children }) => (
  <ScrollableBlockLayout>
    <div>{children}</div>
  </ScrollableBlockLayout>
);
ScrollableBlock.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]),
};
ScrollableBlock.Layout = ScrollableBlockLayout;

export default ScrollableBlock;
