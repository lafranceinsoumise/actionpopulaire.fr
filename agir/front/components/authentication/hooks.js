import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getIsConnected,
} from "@agir/front/globalContext/reducers";

export const useAuthentication = (route) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const isUserAuthenticated = useSelector(getIsConnected);

  if (route.protected === false) {
    return true;
  }

  if (!isSessionLoaded) {
    return null;
  }

  return !!isUserAuthenticated;
};
