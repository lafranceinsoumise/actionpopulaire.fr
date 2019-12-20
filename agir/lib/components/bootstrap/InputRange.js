import React, { useRef } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { animated, useSpring } from "react-spring";
import { useDrag } from "react-use-gesture";

const Container = styled.div`
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
  width: 100%;
  height: 3rem;
  position: relative;
`;

const DraggableContainer = React.forwardRef(
  ({ disabled, children, onDrag }, ref) => {
    const bind = useDrag(({ xy }) => {
      onDrag(xy[0]);
    });

    return (
      <Container ref={ref} {...bind()} disabled={disabled}>
        {children}
      </Container>
    );
  }
);
DraggableContainer.displayName = "DraggableContainer";
DraggableContainer.propTypes = {
  children: PropTypes.node,
  onDrag: PropTypes.func,
  disabled: PropTypes.bool
};
DraggableContainer.defaultProps = {
  onDrag: () => null,
  disabled: false
};

const BaseTrack = styled.div`
  position: absolute;
  background: #bcbcbc;
  border-radius: 0.3rem;
  height: 0.8rem;
  width: 100%;
  padding: 0;
  top: 50%;
  transform: translateY(-50%);
`;

const ActiveTrack = animated(styled.div`
  border-radius: 0.3rem;
  background: ${({ disabled }) => (disabled ? "#858585" : "#913725")};
  margin: 0 auto 0 0;
  padding: 0;
  height: 100%;
`);

const Track = ({ position, disabled }) => {
  return (
    <BaseTrack>
      <ActiveTrack style={{ width: position }} disabled={disabled} />
    </BaseTrack>
  );
};
Track.propTypes = {
  position: PropTypes.any,
  onChange: PropTypes.func,
  disabled: PropTypes.bool
};

Track.defaultProps = {
  position: 0,
  onChange: () => null,
  disabled: false
};

const SliderPointer = animated(styled.div`
  appearance: none;
  position: absolute;

  // background and border
  background: ${({ disabled }) => (disabled ? "#a8a8a8" : "#c9462c")};
  border: 1px solid ${({ disabled }) => (disabled ? "#9a9a9a" : "#b43f27")};
  border-radius: 0;

  // vertical dimensions
  height: 2rem;
  top: 50%;
  outline: none;

  // horizontal dimensions
  width: 1rem;

  // center
  transform: translate(-50%, -50%);
`);

const Slider = ({ position, disabled }) => {
  return <SliderPointer style={{ left: position }} disabled={disabled} />;
};
Slider.propTypes = {
  position: PropTypes.any,
  disabled: PropTypes.bool
};
Slider.defaultProps = {
  position: 0,
  disabled: false
};

const InputRange = ({
  value,
  minValue,
  maxValue,
  step,
  onChange,
  disabled
}) => {
  const valuePerc = (value - minValue) / (maxValue - minValue);
  const ref = useRef();

  const clamp = x => {
    const bounds = ref.current.getBoundingClientRect();
    const val =
      Math.floor(
        (((x - bounds.left) / bounds.width) * (maxValue - minValue)) / step
      ) * step;

    return val < minValue ? minValue : val > maxValue ? maxValue : val;
  };

  const { x } = useSpring({
    x: `${(Number.isNaN(valuePerc) ? 0 : valuePerc) * 100}%`
  });

  const handleChange = x => !disabled && onChange(clamp(x));

  return (
    <DraggableContainer ref={ref} onDrag={handleChange} disabled={disabled}>
      <Track position={x} disabled={disabled} />
      <Slider position={x} disabled={disabled} />
    </DraggableContainer>
  );
};

InputRange.propTypes = {
  value: PropTypes.number,
  minValue: PropTypes.number,
  maxValue: PropTypes.number,
  step: PropTypes.number,
  onChange: PropTypes.func,
  disabled: PropTypes.bool
};

InputRange.defaultProps = {
  value: 0,
  minValue: 0,
  maxValue: 100,
  step: 1,
  onChange: () => null,
  disabled: false
};

export default InputRange;
