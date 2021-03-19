import { useEffect } from "react";
import { useHistory } from "react-router-dom";

export const useCustomBackNavigation = (callback) => {
  const history = useHistory();

  useEffect(() => {
    let unblock = undefined;
    if (history && typeof callback === "function") {
      unblock = history.block(() => {
        callback();
        return false;
      });
    }
    return unblock;
  }, [callback, history]);
};
