import { init, reactRouterV5Instrumentation } from "@sentry/react";
import { Integrations } from "@sentry/tracing";
import { isMatchingPattern } from "@sentry/utils";

import { createBrowserHistory } from "history";
import { matchPath } from "react-router-dom";
import routes from "@agir/front/app/routes.config";
import groupPageRoutes from "@agir/groups/groupPage/GroupPage/routes.config";

const history = createBrowserHistory();

if (process.env.NODE_ENV === "production") {
  init({
    dsn: "https://703ddcbc8ef144c4beebcfbdc25fbd77@erreurs.lafranceinsoumise.fr/3",
    environment: process.env.SENTRY_ENV,
    autoSessionTracking: true,
    release: process.env.SENTRY_RELEASE,
    integrations: [
      new Integrations.BrowserTracing({
        shouldCreateSpanForRequest: (url) => {
          if (isMatchingPattern(url, "/api/session/")) {
            return false;
          }

          return true;
        },
        routingInstrumentation: reactRouterV5Instrumentation(
          history,
          routes.concat(groupPageRoutes),
          matchPath
        ),
      }),
    ],

    // We recommend adjusting this value in production, or using tracesSampler
    // for finer control
    tracesSampleRate: 0.1,

    ignoreErrors: [
      // CUSTOM IGNORE RULES

      // Email link Microsoft Outlook crawler compatibility error
      // cf. https://forum.sentry.io/t/unhandledrejection-non-error-promise-rejection-captured-with-value/14062
      "Non-Error promise rejection captured with value: Object Not Found Matching Id:",

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
    ],
  });
}
