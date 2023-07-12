import { useEffect, useCallback, useState } from "react";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import * as selector from "@agir/front/globalContext/reducers";

import {
  getBookmarkedEmails,
  bookmarkEmails,
  bookmarkEmail,
  AUTHENTICATION,
} from "./common";

export const useAuthentication = (route) => {
  const isSessionLoaded = useSelector(selector.getIsSessionLoaded);
  const authentication = useSelector(selector.getAuthentication);

  if (route.neededAuthentication === AUTHENTICATION.NONE) {
    return true;
  }

  if (!isSessionLoaded) {
    return null;
  }

  return authentication >= route.neededAuthentication;
};

export const useBookmarkedEmails = () => {
  const isSessionLoaded = useSelector(selector.getIsSessionLoaded);
  const legacyBookmarkedEmails = useSelector(selector.getBookmarkedEmails);
  const [bookmarkedEmails, setBookmarkedEmails] = useState(
    getBookmarkedEmails(),
  );

  useEffect(() => {
    if (
      isSessionLoaded &&
      legacyBookmarkedEmails.length > 0 &&
      bookmarkedEmails.length === 0
    ) {
      setBookmarkedEmails(bookmarkEmails(legacyBookmarkedEmails));
    }
  }, [bookmarkedEmails.length, isSessionLoaded, legacyBookmarkedEmails]);

  const addBookmarkedEmail = useCallback((email) => {
    setBookmarkedEmails(bookmarkEmail(email));
  }, []);

  return [bookmarkedEmails, addBookmarkedEmail];
};
