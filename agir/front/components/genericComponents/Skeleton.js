import style from "@agir/front/genericComponents/_variables.scss";
import PropTypes from "prop-types";
import React from "react";

const Skeleton = ({ boxes }) => (
  <>
    {[...Array(boxes).keys()].map((key) => (
      <div
        key={key}
        style={{
          backgroundColor: style.black50,
          height: "177px",
          marginBottom: "32px",
        }}
      />
    ))}
  </>
);

Skeleton.propTypes = {
  boxes: PropTypes.number,
};

Skeleton.defaultProps = {
  boxes: 3,
};

export default Skeleton;
