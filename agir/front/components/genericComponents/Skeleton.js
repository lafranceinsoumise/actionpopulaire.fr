import style from "@agir/front/genericComponents/_variables.scss";
import PropTypes from "prop-types";
import React from "react";

const Skeleton = ({ boxes, ...props }) => (
  <>
    {[...Array(boxes).keys()].map((key) => (
      <div
        key={key}
        {...props}
        style={{
          backgroundColor: style.black50,
          height: "177px",
          marginBottom: "32px",
          ...(props.style || {}),
        }}
      />
    ))}
  </>
);

Skeleton.propTypes = {
  boxes: PropTypes.number,
  style: PropTypes.object,
};

Skeleton.defaultProps = {
  boxes: 3,
};

export default Skeleton;
