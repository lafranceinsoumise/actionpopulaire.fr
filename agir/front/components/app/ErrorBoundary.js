import PropTypes from "prop-types";
import React from "react";
import { ErrorBoundary as SentryErrorBoundary } from "@sentry/react";

import generateLogger from "@agir/lib/utils/logger";

const logger = generateLogger(__filename);

class DevErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      errorMessage: "",
    };
  }

  static getDerivedStateFromError(error) {
    return {
      errorMessage: error.toString(),
    };
  }

  componentDidCatch(error, info) {
    logger.debug(error, info);
  }

  render() {
    const { children, Fallback: CustomFallback } = this.props;
    const { errorMessage } = this.state;

    if (!errorMessage) {
      return children;
    }

    if (CustomFallback) {
      return <CustomFallback {...this.props} errorMessage={errorMessage} />;
    }

    return (
      <div>
        <h2>Erreur</h2>
        {process.env.NODE_ENV === "production" ? null : <p>{errorMessage}</p>}
      </div>
    );
  }
}

const ProdErrorBoundary = (props) => {
  const { children, Fallback: CustomFallback } = props;

  const fallback = ({ error }) => {
    const errorMessage = error.toString();

    if (CustomFallback) {
      return <CustomFallback {...props} errorMessage={errorMessage} />;
    } else {
      return (
        <div>
          <h2>
            Une erreur est survenue. Nous faisons notre possible pour la
            corriger.
          </h2>
        </div>
      );
    }
  };

  return (
    <SentryErrorBoundary fallback={fallback}>{children}</SentryErrorBoundary>
  );
};

DevErrorBoundary.propTypes = ProdErrorBoundary.propTypes = {
  children: PropTypes.node,
  Fallback: PropTypes.oneOfType([PropTypes.func, PropTypes.element]),
};

let ErrorBoundary;
if (process.env.NODE_ENV === "production") {
  ErrorBoundary = ProdErrorBoundary;
} else {
  ErrorBoundary = DevErrorBoundary;
}

export default ErrorBoundary;
