import * as Sentry from "@sentry/react";
import { Integrations } from "@sentry/tracing";
import { isMatchingPattern } from "@sentry/utils";

import { createBrowserHistory } from "history";
import { matchPath } from "react-router-dom";
import routes from "@agir/front/app/routes.config";
import groupPageRoutes from "@agir/groups/groupPage/GroupPage/routes.config";

const history = createBrowserHistory();

let urlMap = {};
let isFirstCallToSession = true;
const origins = ["localhost", /^\//];

if (process.env.NODE_ENV === "production") {
  Sentry.init({
    dsn:
      "https://208ef75bce0a46f6b20b69c2952957d7@erreurs.lafranceinsoumise.fr/4",
    autoSessionTracking: true,
    release: process.env.SENTRY_RELEASE,
    integrations: [
      new Integrations.BrowserTracing({
        shouldCreateSpanForRequest: (url) => {
          if (isFirstCallToSession && isMatchingPattern(url, "/api/session/")) {
            isFirstCallToSession = false;
            return false;
          }

          if (typeof urlMap[url] !== "undefined") {
            return urlMap[url];
          }

          urlMap[url] =
            origins.some((origin) => isMatchingPattern(url, origin)) &&
            !isMatchingPattern(url, "sentry_key");
          return urlMap[url];
        },
        routingInstrumentation: Sentry.reactRouterV5Instrumentation(
          history,
          routes.concat(groupPageRoutes),
          matchPath
        ),
      }),
    ],

    // We recommend adjusting this value in production, or using tracesSampler
    // for finer control
    tracesSampleRate: 1.0,
  });
}
