import {
  init,
  reactRouterV5Instrumentation,
  Replay,
  BrowserTracing,
} from "@sentry/react";
import { isMatchingPattern } from "@sentry/utils";

import { createBrowserHistory } from "history";
import { matchPath } from "react-router-dom";
import routes from "@agir/front/app/routes.config";
import groupPageRoutes from "@agir/groups/groupPage/GroupPage/routes.config";

const history = createBrowserHistory();

if (process.env.NODE_ENV === "production") {
  init({
    dsn: "https://f922ec88796e450191953c4c4f0389b7@o4504333216841728.ingest.sentry.io/4504333336510464",
    environment: process.env.SENTRY_ENV,
    autoSessionTracking: true,
    release: process.env.SENTRY_RELEASE,
    integrations: [
      new BrowserTracing({
        shouldCreateSpanForRequest: (url) => {
          if (isMatchingPattern(url, "/api/session/")) {
            return false;
          }

          return true;
        },
        routingInstrumentation: reactRouterV5Instrumentation(
          history,
          routes.concat(groupPageRoutes),
          matchPath,
        ),
      }),
      new Replay(),
    ],

    // We recommend adjusting this value in production, or using tracesSampler
    // for finer control
    tracesSampleRate: 0.1,

    // This sets the sample rate to be 0.5%. You may want this to be 100% while
    // in development and sample at a lower rate in production
    replaysSessionSampleRate: 0.005,
    // If the entire session is not sampled, use the below sample rate to sample
    // sessions when an error occurs.
    replaysOnErrorSampleRate: 1.0,

    ignoreErrors: [
      // CUSTOM IGNORE RULES

      // Email link Microsoft Outlook crawler compatibility error
      // cf. https://forum.sentry.io/t/unhandledrejection-non-error-promise-rejection-captured-with-value/14062
      "Non-Error promise rejection captured",

      // COMMON IGNORE RULES
      // cf. https://docs.sentry.io/clients/javascript/tips/

      // Random plugins/extensions
      "top.GLOBALS",
      // See: http://blog.errorception.com/2012/03/tale-of-unfindable-js-error.html
      "originalCreateNotification",
      "canvas.contentDocument",
      "MyApp_RemoveAllHighlights",
      "http://tt.epicplay.com",
      "Can't find variable: ZiteReader",
      "jigsaw is not defined",
      "ComboSearch is not defined",
      "http://loading.retry.widdit.com/",
      "atomicFindClose",
      "/change_ua/",
      // Facebook borked
      "fb_xd_fragment",
      // ISP "optimizing" proxy - `Cache-Control: no-transform` seems to
      // reduce this. (thanks @acdha)
      // See http://stackoverflow.com/questions/4113268
      "bmi_SafeAddOnload",
      "EBCallBackMessageReceived",
      // See http://toolbar.conduit.com/Developer/HtmlAndGadget/Methods/JSInjection.aspx
      "conduitPage",
      // see https://stackoverflow.com/questions/49384120/resizeobserver-loop-limit-exceeded
      "ResizeObserver loop limit exceeded",
      "ResizeObserver loop completed with undelivered notifications.",
    ],
    denyUrls: [
      // Facebook flakiness
      /graph\.facebook\.com/i,
      // Facebook blocked
      /connect\.facebook\.net\/en_US\/all\.js/i,
      // Woopra flakiness
      /eatdifferent\.com\.woopra-ns\.com/i,
      /static\.woopra\.com\/js\/woopra\.js/i,
      // Chrome extensions
      /extensions\//i,
      /^chrome:\/\//i,
      // Other plugins
      /127\.0\.0\.1:4001\/isrunning/i, // Cacaoweb
      /webappstoolbarba\.texthelp\.com\//i,
      /metrics\.itunes\.apple\.com\.edgesuite\.net\//i,
    ],
  });
}
