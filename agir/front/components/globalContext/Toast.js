import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo } from "react";
import styled from "styled-components";

import { ToastContainer, toast } from "react-toastify";
import {
  useSelector,
  useDispatch,
} from "@agir/front/globalContext/GlobalContext";
import { getToasts, getUser } from "@agir/front/globalContext/reducers";
import { clearToast } from "@agir/front/globalContext/actions";
import SoftLoginModal, {
  SOFT_LOGIN_MODAL_TAGS,
} from "@agir/front/authentication/SoftLoginModal";

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
  max-width: calc(100vw - 32px);
  width: 650px;
  left: 16px;
  right: 16px;

  @media only screen and (max-width: ${style.collapse}px) {
    bottom: 144px;
  }

  .Toastify__toast {
    cursor: auto;
    box-sizing: border-box;
    padding: 1rem 1.5rem;
    background-color: white;
    font-family: ${style.fontFamilyBase};
    line-height: 1.12;
    color: ${style.black1000};
    border-left: 6px solid ${style.black1000};
  }

  .Toastify__toast--error {
    border-left: 6px solid ${style.redNSP};
  }

  .Toastify__toast--success {
    border-left: 6px solid ${style.green500};
  }

  .Toastify__toast-body {
    padding-right: 14px;
    font-size: inherit;
    line-height: inherit;
    color: inherit;
    opacity: 1;
  }
`;

const CloseButton = ({ closeToast }) => (
  <button
    type="button"
    style={{
      backgroundColor: "transparent",
      width: "24px",
      height: "24px",
      border: 0,
      padding: 0,
      cursor: "pointer",
    }}
    onClick={closeToast}
  >
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M16.4702 7.52977C16.7299 7.78946 16.7299 8.21052 16.4702 8.47022L8.47019 16.4702C8.21049 16.7299 7.78943 16.7299 7.52973 16.4702C7.27004 16.2105 7.27004 15.7895 7.52973 15.5298L15.5297 7.52977C15.7894 7.27007 16.2105 7.27007 16.4702 7.52977Z"
        fill="#000A2C"
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M7.52973 7.52977C7.78943 7.27007 8.21049 7.27007 8.47019 7.52977L16.4702 15.5298C16.7299 15.7895 16.7299 16.2105 16.4702 16.4702C16.2105 16.7299 15.7894 16.7299 15.5297 16.4702L7.52973 8.47022C7.27004 8.21052 7.27004 7.78946 7.52973 7.52977Z"
        fill="#000A2C"
      />
      <rect x="0.5" y="0.5" width="23" height="23" rx="11.5" stroke="#000A2C" />
    </svg>
  </button>
);
CloseButton.propTypes = {
  closeToast: PropTypes.func.isRequired,
};
export const Toast = (props) => {
  const { toasts = [], onClear } = props;

  useEffect(() => {
    toasts.forEach((t) => {
      toast(
        t.html ? (
          <div dangerouslySetInnerHTML={{ __html: t.message }} />
        ) : (
          t.message
        ),
        {
          closeOnClick: false,
          position: toast.POSITION.BOTTOM_LEFT,
          ...t,
          type: TOAST_TYPES[t.type.toUpperCase()],
          onClose: () => {
            typeof t.onClose === "function" && t.onClose();
            onClear(t.toastId);
          },
        },
      );
    });
  }, [toasts, onClear]);

  return <StyledContainer closeButton={CloseButton} />;
};

const ConnectedToast = (props) => {
  const allToasts = useSelector(getToasts);
  const user = useSelector(getUser);
  const dispatch = useDispatch();
  const handleClear = useCallback(
    (toastId) => {
      dispatch(clearToast(toastId));
    },
    [dispatch],
  );

  const [softLoginToast, toasts] = useMemo(() => {
    let softLoginToast = null;
    const toasts = allToasts.filter((toast) => {
      if (
        toast.tags &&
        SOFT_LOGIN_MODAL_TAGS.some((tag) => toast.tags.includes(tag))
      ) {
        softLoginToast = toast;
        return false;
      }
      return true;
    });
    return [softLoginToast, toasts];
  }, [allToasts]);

  return (
    <>
      <SoftLoginModal
        user={user}
        shouldShow={!!user && !!softLoginToast}
        onClose={() => handleClear(softLoginToast.toastId)}
        data={softLoginToast}
      />
      <Toast {...props} toasts={toasts} onClear={handleClear} />
    </>
  );
};

Toast.propTypes = {
  toasts: PropTypes.arrayOf(
    PropTypes.shape({
      toastId: PropTypes.string.isRequired,
      message: PropTypes.string.isRequired,
      html: PropTypes.bool,
      type: PropTypes.oneOf(Object.keys(TOAST_TYPES)),
      autoClose: PropTypes.oneOfType([PropTypes.bool, PropTypes.number]),
      closeOnClick: PropTypes.bool,
    }),
  ),
  onClear: PropTypes.func,
  autoClose: PropTypes.bool,
};
export default ConnectedToast;
