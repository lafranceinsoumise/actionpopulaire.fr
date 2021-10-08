import PropTypes from "prop-types";
import React, { useEffect } from "react";
import { usePrevious } from "react-use";
import styled from "styled-components";
import * as Sentry from "@sentry/react";

import style from "@agir/front/genericComponents/_variables.scss";

import background from "@agir/front/genericComponents/images/illustration-404.svg";
import { useIsOffline } from "@agir/front/offline/hooks";
import { useAppLoader } from "@agir/front/app/hooks";

import TopBar from "@agir/front/allPages/TopBar/TopBar";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import illustration from "./illustration.svg";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: calc(100vh - 74px);
  position: relative;
  overflow: auto;
  background-image: url("${background}");
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  padding: 28px 14px;
`;

const InterrogationMark = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 56px;
  font-size: 30px;
  background-color: ${style.secondary500};
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-weight: 500;
`;

const PageStyle = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

const OfflineBlock = styled.div`
  & > * {
    margin: 0 auto;
    padding: 0 16px;
  }

  & > h1 {
    font-size: 20px;
  }
`;

export const NotFoundPage = ({
  isTopBar = true,
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

  if (!isOffline) {
    Sentry.addBreadcrumb({
      category: "logging",
      message: `React shows a 'Not found page' : ${window.location.pathname}`,
      level: Sentry.Severity.Debug,
    });
  }

  return (
    <PageStyle>
      {isTopBar && (
        <>
          <TopBar />
          <Spacer size="74px" />
        </>
      )}
      <Container>
        {isOffline ? (
          <OfflineBlock>
            <img
              src={illustration}
              width="163"
              height="175"
              style={{ marginBottom: "32px" }}
            />
            <h1 style={{ marginBottom: "8px" }}>Pas de connexion</h1>
            <p>
              Connectez-vous à un
              <br />
              réseau Wi-Fi ou mobile
            </p>
          </OfflineBlock>
        ) : (
          <>
            <InterrogationMark>?</InterrogationMark>
            <h1 style={{ textAlign: "center", fontSize: "26px" }}>
              {title + " "}introuvable
            </h1>
            <span>{subtitle + " "}n’existe pas ou plus</span>
            <Button
              style={{ maxWidth: 450, marginTop: "2rem" }}
              color="primary"
              block
              link
              route="events"
            >
              Retourner à l'accueil
            </Button>
            <span style={{ marginTop: "2rem", backgroundColor: "#fff" }}>
              ou consulter le{" "}
              <a href="https://infos.actionpopulaire.fr/">centre d'aide</a>
            </span>
          </>
        )}
      </Container>
    </PageStyle>
  );
};
NotFoundPage.propTypes = {
  isTopBar: PropTypes.bool,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  reloadOnReconnection: PropTypes.bool,
};
export default NotFoundPage;
