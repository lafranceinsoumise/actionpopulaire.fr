import * as Sentry from "@sentry/react";
import { Integrations } from "@sentry/tracing";

if (process.env.NODE_ENV === "production") {
  Sentry.init({
    dsn:
      "https://208ef75bce0a46f6b20b69c2952957d7@erreurs.lafranceinsoumise.fr/4",
    autoSessionTracking: true,
    release: process.env.SENTRY_RELEASE,
    integrations: [new Integrations.BrowserTracing()],

    // We recommend adjusting this value in production, or using tracesSampler
    // for finer control
    tracesSampleRate: 1.0,
  });
}
