import PropTypes from "prop-types";
import React, { useCallback, useEffect } from "react";
import { ToastContainer, toast } from "react-toastify";
import {
  useSelector,
  useDispatch,
} from "@agir/front/globalContext/GlobalContext";
import { getToasts } from "@agir/front/globalContext/reducers";
import { clearToast } from "@agir/front/globalContext/actions";

import "react-toastify/dist/ReactToastify.min.css";

export const TOAST_TYPES = {
  DEFAULT: toast.TYPE.DEFAULT,
  DEBUG: toast.TYPE.DEFAULT,
  INFO: toast.TYPE.INFO,
  SUCCESS: toast.TYPE.SUCCESS,
  WARNING: toast.TYPE.WARNING,
  ERROR: toast.TYPE.ERROR,
  DANGER: toast.TYPE.ERROR,
};

export const Toast = (props) => {
  const { toasts = [], onClear } = props;

  useEffect(() => {
    toasts.forEach((t) => {
      toast(t.message, {
        toastId: t.toastId,
        type: TOAST_TYPES[t.type.toUpperCase()],
        onClose: () => onClear(t),
      });
    });
  }, [toasts, onClear]);

  return <ToastContainer />;
};

const ConnectedToast = (props) => {
  const toasts = useSelector(getToasts);
  const dispatch = useDispatch();
  const handleClear = useCallback(
    ({ toastId }) => {
      dispatch(clearToast(toastId));
    },
    [dispatch]
  );
  return <Toast {...props} toasts={toasts} onClear={handleClear} />;
};

Toast.propTypes = {
  toasts: PropTypes.arrayOf(
    PropTypes.shape({
      toastId: PropTypes.string.isRequired,
      message: PropTypes.string.isRequired,
      type: PropTypes.oneOf(Object.keys(TOAST_TYPES)),
    })
  ),
  onClear: PropTypes.func,
};
export default ConnectedToast;
