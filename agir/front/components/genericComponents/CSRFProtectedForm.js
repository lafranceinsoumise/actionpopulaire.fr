import React from "react";
import PropTypes from "prop-types";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getCsrfToken } from "@agir/front/globalContext/reducers";

const CSRFProtectedForm = ({ children, ...props }) => {
  const csrfToken = useSelector(getCsrfToken);

  return (
    <form {...props}>
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken || ""} />
      {children}
    </form>
  );
};
CSRFProtectedForm.propTypes = {
  children: PropTypes.node,
};

export default CSRFProtectedForm;
