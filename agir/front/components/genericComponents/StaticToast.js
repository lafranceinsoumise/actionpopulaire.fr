import PropTypes from "prop-types";
import styled from "styled-components";

const StaticToast = styled.div`
  display: flex;
  padding: 1rem;
  border: 1px solid ${(props) => props.theme.text500};
  border-radius: ${(props) => props.theme.borderRadius};
  position: relative;
  margin-top: 2rem;
  background: linear-gradient(
    90deg,
    ${(props) => {
        if (!props.$color) {
          return props.theme.error500;
        }
        return props.theme[props.$color] || props.$color;
      }}
      6px,
    transparent 6px,
    transparent
  );
`;
StaticToast.propTypes = {
  $color: PropTypes.string,
};
export default StaticToast;
