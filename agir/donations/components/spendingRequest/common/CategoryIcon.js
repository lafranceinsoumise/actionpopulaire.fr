import PropTypes from "prop-types";
import React from "react";

import FaIcon from "@agir/front/genericComponents/FaIcon";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const CategoryIcon = ({ category, size, ...rest }) => {
  if (!category || !category.icon) {
    return null;
  }

  return category.icon.startsWith("fa:") ? (
    <FaIcon
      {...rest}
      title={category.name}
      icon={category.icon.replace("fa:", "")}
      size={size}
    />
  ) : (
    <RawFeatherIcon
      {...rest}
      title={category.name}
      width={size}
      height={size}
      name={category.icon}
    />
  );
};

CategoryIcon.propTypes = {
  category: PropTypes.shape({ icon: PropTypes.string, name: PropTypes.string }),
  size: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default CategoryIcon;
