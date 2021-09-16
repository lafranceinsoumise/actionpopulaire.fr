import PropTypes from "prop-types";
import React, { Suspense } from "react";

import { lazy } from "@agir/front/app/utils";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getUser,
} from "@agir/front/globalContext/reducers";
import { useMobileApp } from "@agir/front/app/hooks";

const Footer = lazy(() => import("./Footer"));

const ConnectedFooter = (props) => {
  const { hideBanner, displayOnMobileApp } = props;

  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);
  const { isMobileApp } = useMobileApp();

  if (isMobileApp && !displayOnMobileApp) {
    return null;
  }

  if (!isSessionLoaded) {
    return null;
  }

  return (
    <Suspense fallback={<div />}>
      <Footer
        {...props}
        isSignedIn={!!user}
        isMobileApp={isMobileApp}
        hasBanner={!hideBanner && !user}
      />
    </Suspense>
  );
};

ConnectedFooter.propTypes = {
  isSignedIn: PropTypes.bool,
  hideBanner: PropTypes.bool,
  displayOnMobileApp: PropTypes.bool,
};

export default ConnectedFooter;
