import PropTypes from "prop-types";
import React, { useEffect } from "react";
import { usePrevious } from "react-use";
import styled from "styled-components";

import { useIsOffline } from "@agir/front/offline/hooks";
import { useAppLoader } from "@agir/front/app/hooks";

import illustration from "./illustration.svg";
import ErrorPage from "@agir/front/errorPage/ErrorPage";

const OfflineBlock = styled.div`
  text-align: center;

  & > * {
    margin: 0 auto;
    padding: 0 1rem;
  }

  & > h1 {
    font-size: 1.25rem;
  }
`;

export const NotFoundPage = ({
  hasTopBar = true,
  title = "Page",
  subtitle = "Cette page",
  reloadOnReconnection = true,
}) => {
  const isOffline = useIsOffline();
  const wasOffline = usePrevious(isOffline);

  useAppLoader();

  useEffect(() => {
    reloadOnReconnection &&
      wasOffline &&
      !isOffline &&
      window.location.reload();
  }, [reloadOnReconnection, isOffline, wasOffline]);

  if (isOffline === null) return null;

  if (isOffline) {
    return (
      <ErrorPage hasTopBar={hasTopBar}>
        <OfflineBlock>
          <img
            src={illustration}
            width="163"
            height="175"
            style={{ marginBottom: "2rem" }}
          />
          <h2 style={{ marginBottom: ".5rem" }}>Pas de connexion</h2>
          <p>
            Connectez-vous à un
            <br />
            réseau Wi-Fi ou mobile
          </p>
        </OfflineBlock>
      </ErrorPage>
    );
  }

  return (
    <ErrorPage
      icon="?"
      title={`${title} introuvable`.trim()}
      subtitle={`${subtitle} n’existe pas ou plus`.trim()}
      hasReload={false}
      hasTopBar={hasTopBar}
    />
  );
};

NotFoundPage.propTypes = {
  hasTopBar: PropTypes.bool,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  reloadOnReconnection: PropTypes.bool,
};

export default NotFoundPage;
