import Cookies from "js-cookie";

export const AUTHENTICATION = {
  NONE: 0,
  SOFT: 1,
  HARD: 2,
};

const BOOKMARKED_EMAILS_COOKIE_NAME = "AP_bookmarkedEmails";
const BOOKMARKED_EMAILS_COOKIE_OPTIONS = {
  expires: 365,
  secure: process.env.NODE_ENV !== "development",
  sameSite: "Strict",
};

export const getBookmarkedEmails = () => {
  let cookieData = Cookies.getJSON(BOOKMARKED_EMAILS_COOKIE_NAME);
  if (!cookieData) {
    return [];
  }
  return cookieData;
};

export const bookmarkEmails = (emails) => {
  Cookies.set(
    BOOKMARKED_EMAILS_COOKIE_NAME,
    emails,
    BOOKMARKED_EMAILS_COOKIE_OPTIONS
  );

  return emails;
};

export const bookmarkEmail = (email) => {
  const bookmarkedEmails = getBookmarkedEmails();
  const cookieData = [email, ...bookmarkedEmails.filter((e) => e !== email)];

  Cookies.set(
    BOOKMARKED_EMAILS_COOKIE_NAME,
    cookieData,
    BOOKMARKED_EMAILS_COOKIE_OPTIONS
  );

  return cookieData;
};
