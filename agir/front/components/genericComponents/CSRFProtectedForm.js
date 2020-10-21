import React from "react";
import PropTypes from "prop-types";
import { useGlobalContext } from "@agir/front/genericComponents/GobalContext";

const CSRFProtectedForm = ({ children, ...props }) => {
  const { csrfToken } = useGlobalContext();

  return (
    <form {...props}>
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
      {children}
    </form>
  );
};
CSRFProtectedForm.propTypes = {
  children: PropTypes.node,
};

export default CSRFProtectedForm;
