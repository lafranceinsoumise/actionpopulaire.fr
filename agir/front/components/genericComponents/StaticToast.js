import PropTypes from "prop-types";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

const StaticToast = styled.div`
  display: flex;
  padding: 1rem;
  border: 1px solid ${style.black500};
  border-radius: ${style.borderRadius};
  position: relative;
  margin-top: 2rem;
  background: linear-gradient(
    90deg,
    ${(props) => {
        if (!props.$color) {
          return props.theme.redNSP;
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
