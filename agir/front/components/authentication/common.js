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
  let cookieData = Cookies.get(BOOKMARKED_EMAILS_COOKIE_NAME);
  cookieData = cookieData && JSON.parse(cookieData);
  return cookieData || [];
};

export const bookmarkEmails = (emails) => {
  Cookies.set(
    BOOKMARKED_EMAILS_COOKIE_NAME,
    JSON.stringify(emails),
    BOOKMARKED_EMAILS_COOKIE_OPTIONS
  );

  return emails;
};

export const bookmarkEmail = (email) => {
  const bookmarkedEmails = getBookmarkedEmails();
  const cookieData = JSON.stringify([
    email,
    ...bookmarkedEmails.filter((e) => e !== email),
  ]);

  Cookies.set(
    BOOKMARKED_EMAILS_COOKIE_NAME,
    cookieData,
    BOOKMARKED_EMAILS_COOKIE_OPTIONS
  );

  return cookieData;
};

export const getMobileOS = () => {
  let userAgent = navigator.userAgent || navigator.vendor || window.opera;

  // Windows Phone must come first because its UA also contains "Android"
  if (/windows phone/i.test(userAgent)) {
    return "Windows Phone";
  }
  if (/android/i.test(userAgent)) {
    return "android";
  }
  if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
    return "iOS";
  }
  return "unknown";
};
