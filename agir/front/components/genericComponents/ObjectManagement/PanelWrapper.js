import { animated } from "@react-spring/web";
import styled from "styled-components";

export const PanelWrapper = styled(animated.div)`
  position: absolute;
  top: 0;
  left: 0;
  padding: 2rem;
  background-color: ${(props) => props.theme.background0};
  width: 100%;
  height: 100%;
  box-shadow: ${(props) => props.theme.elaborateShadow};
  will-change: transform;
  overflow-y: auto;
  z-index: ${(props) => props.theme.zindexPanel};
`;

export default PanelWrapper;
