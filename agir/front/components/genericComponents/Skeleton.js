import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

const Bone = styled.div`
  background-color: ${(props) => props.theme.black50};
  height: 177px;
  margin-bottom: 32px;
`;

const Skeleton = ({ boxes = 3, ...props }) => {
  const Bones = useMemo(() => {
    let result = [];
    for (let key = boxes; key > 0; key -= 1) {
      result.push(Bone);
    }
    return result;
  }, [boxes]);

  return Bones.map((Bone, key) => <Bone key={key} {...props} />);
};

Skeleton.propTypes = {
  boxes: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default Skeleton;
