import React, { useRef, useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { animated, useSpring } from "@react-spring/web";
import { useDrag } from "@use-gesture/react";
import { useThrottle } from "@agir/lib/utils/hooks";

const Container = styled.div`
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
  width: 100%;
  height: 3rem;
  position: relative;
`;

const DraggableContainer = React.forwardRef(
  ({ disabled, children, onDrag }, ref) => {
    const bind = useDrag(({ xy, last }) => {
      onDrag(xy[0], last);
    });

    return (
      <Container ref={ref} {...bind()} disabled={disabled}>
        {children}
      </Container>
    );
  },
);
DraggableContainer.displayName = "DraggableContainer";
DraggableContainer.propTypes = {
  children: PropTypes.node,
  onDrag: PropTypes.func,
  disabled: PropTypes.bool,
};
DraggableContainer.defaultProps = {
  onDrag: () => null,
  disabled: false,
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
  disabled: PropTypes.bool,
};

Track.defaultProps = {
  position: 0,
  onChange: () => null,
  disabled: false,
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
  disabled: PropTypes.bool,
};
Slider.defaultProps = {
  position: 0,
  disabled: false,
};

const InputRange = ({
  value,
  minValue,
  maxValue,
  step,
  onChange,
  disabled,
}) => {
  const [dragValue, setDragValue] = useState(null);
  const displayValue = dragValue === null ? value : dragValue;
  const valueInPercent = (displayValue - minValue) / (maxValue - minValue);

  const containerRef = useRef();
  const throttledOnChange = useThrottle(onChange, 100);

  const valueFromPosition = (x) => {
    const bounds = containerRef.current.getBoundingClientRect();
    const val = ((x - bounds.left) / bounds.width) * (maxValue - minValue);
    return val < minValue ? minValue : val > maxValue ? maxValue : val;
  };

  const clampValue = (val) => {
    val = Math.round(val / step) * step;

    return val < minValue ? minValue : val > maxValue ? maxValue : val;
  };

  const { x } = useSpring({
    x: `${(Number.isNaN(valueInPercent) ? 0 : valueInPercent) * 100}%`,
  });

  const handleChange = (x, stoppedDragging) => {
    if (!disabled) {
      const visibleValue = valueFromPosition(x);
      const newValue = clampValue(visibleValue);

      if (stoppedDragging) {
        onChange(newValue);
        setDragValue(null);
      } else {
        throttledOnChange(newValue);
        setDragValue(visibleValue);
      }
    }
  };

  return (
    <DraggableContainer
      ref={containerRef}
      onDrag={handleChange}
      disabled={disabled}
    >
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
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

InputRange.defaultProps = {
  value: 0,
  minValue: 0,
  maxValue: 100,
  step: 1,
  disabled: false,
};

export default InputRange;
