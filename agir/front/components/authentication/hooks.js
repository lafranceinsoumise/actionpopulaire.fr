import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getAuthentication,
} from "@agir/front/globalContext/reducers";

export const useAuthentication = (route) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const authentication = useSelector(getAuthentication);

  if (!isSessionLoaded) {
    return null;
  }

  return authentication >= route.neededAuthentication;
};
