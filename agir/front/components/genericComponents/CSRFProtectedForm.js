import React from "react";
import PropTypes from "prop-types";
import useSWRImmutable from "swr/immutable";

const CSRFProtectedForm = ({ children, ...props }) => {
  const { data } = useSWRImmutable("/api/csrf/");

  return (
    <form {...props}>
      <input
        type="hidden"
        name="csrfmiddlewaretoken"
        value={data?.csrfToken || ""}
      />
      {children}
    </form>
  );
};
CSRFProtectedForm.propTypes = {
  children: PropTypes.node,
};

export default CSRFProtectedForm;
