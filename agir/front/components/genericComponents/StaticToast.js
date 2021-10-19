import PropTypes from "prop-types";
import styled from "styled-components";

const StaticToast = styled.div`
  display: flex;
  padding: 1rem;
  border: 1px solid #000a2c;
  position: relative;
  margin-top: 2rem;
  background: linear-gradient(
    90deg,
    ${(props) => props.$color || props.theme.redNSP} 6px,
    transparent 6px,
    transparent
  );
`;
StaticToast.propTypes = {
  $color: PropTypes.string,
};
export default StaticToast;
