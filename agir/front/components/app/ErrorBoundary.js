import PropTypes from "prop-types";
import React from "react";
import { ErrorBoundary as SentryErrorBoundary } from "@sentry/react";

import ErrorPage from "@agir/front/errorPage/ErrorPage";

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

    return <ErrorPage errorMessage={errorMessage} />;
  }
}

const ProdErrorBoundary = (props) => {
  const { children, Fallback: CustomFallback } = props;

  const fallback = ({ error }) =>
    CustomFallback ? (
      <CustomFallback {...props} errorMessage={error.toString()} />
    ) : (
      <ErrorPage />
    );

  return (
    <SentryErrorBoundary fallback={fallback}>{children}</SentryErrorBoundary>
  );
};

DevErrorBoundary.propTypes = ProdErrorBoundary.propTypes = {
  children: PropTypes.node,
  Fallback: PropTypes.oneOfType([PropTypes.func, PropTypes.element]),
};

const ErrorBoundary =
  process.env.NODE_ENV === "production" ? ProdErrorBoundary : DevErrorBoundary;

export default ErrorBoundary;
