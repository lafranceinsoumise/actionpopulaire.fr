import { animated } from "@react-spring/web";
import styled from "styled-components";
import * as style from "@agir/front/genericComponents/_variables.scss";

export const PanelWrapper = styled(animated.div)`
  position: absolute;
  top: 0;
  left: 0;
  padding: 2rem;
  background-color: white;
  width: 100%;
  height: 100%;
  box-shadow: ${style.elaborateShadow};
  will-change: transform;
  overflow-y: auto;
  z-index: ${style.zindexPanel};
`;

export default PanelWrapper;
