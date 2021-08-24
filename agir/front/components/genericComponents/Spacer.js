import PropTypes from "prop-types";
import styled from "styled-components";

const getHeight = ({ axis, size }) => {
  const space = typeof size === "number" ? size + "px" : size;
  return axis === "x" ? "1px" : space;
};
const getWidth = ({ axis, size }) => {
  const space = typeof size === "number" ? size + "px" : size;
  return axis === "y" ? "1px" : space;
};

const Spacer = styled.span.attrs((props) => ({
  $width: getWidth(props),
  $height: getHeight(props),
  "aria-hidden": "true",
}))`
  display: block;
  margin: 0;
  padding: 0;
  line-height: 0;
  width: ${({ $width }) => $width};
  min-width: ${({ $width }) => $width};
  height: ${({ $height }) => $height};
  min-height: ${({ $height }) => $height};
`;

export const InlineSpacer = styled(Spacer)`
  display: inline-block;
`;

Spacer.propTypes = InlineSpacer.propTypes = {
  axis: PropTypes.oneOf(["x", "y"]),
  size: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default Spacer;
