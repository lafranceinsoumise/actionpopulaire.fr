import { useCallback } from "react";
import { useDispatch } from "@agir/front/globalContext/GlobalContext";
import { addToasts } from "@agir/front/globalContext/actions";

export const useToast = () => {
  const dispatch = useDispatch();

  const sendToast = useCallback(
    (message, type, config) => {
      const toast = {
        message: message,
        type: type || "DEFAULT",
        ...config,
      };
      dispatch(addToasts(toast));
    },
    [dispatch],
  );

  return sendToast;
};
