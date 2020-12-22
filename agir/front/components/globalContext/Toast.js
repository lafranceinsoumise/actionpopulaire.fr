import PropTypes from "prop-types";
import React, { useCallback, useEffect } from "react";
import styled from "styled-components";

import { ToastContainer, toast } from "react-toastify";
import {
  useSelector,
  useDispatch,
} from "@agir/front/globalContext/GlobalContext";
import { getToasts } from "@agir/front/globalContext/reducers";
import { clearToast } from "@agir/front/globalContext/actions";

import style from "@agir/front/genericComponents/_variables.scss";
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

const StyledContainer = styled(ToastContainer)`
  .Toastify__toast-container {
  }
  .Toastify__toast {
    box-sizing: border-box;
    padding: 1rem 1.5rem;
    background-color: ${style.black1000};
    color: white;
    font-family: ${style.fontFamilyBase};
    font-weight: 500;
    line-height: 1.12;
  }
  .Toastify__toast--error {
    background-color: ${style.redNSP};
  }
  .Toastify__toast--success {
    background-color: ${style.green500};
  }
  .Toastify__toast-body,
  .Toastify__close-button {
    font-size: inherit;
    line-height: inherit;
    color: inherit;
    opacity: 1;
  }
  .Toastify__progress-bar {
  }
`;

export const Toast = (props) => {
  const { toasts = [], onClear } = props;

  useEffect(() => {
    toasts.forEach((t) => {
      toast(t.message, {
        toastId: t.toastId,
        position: toast.POSITION.TOP_CENTER,
        type: TOAST_TYPES[t.type.toUpperCase()],
        onClose: () => onClear(t),
      });
    });
  }, [toasts, onClear]);

  return <StyledContainer />;
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
