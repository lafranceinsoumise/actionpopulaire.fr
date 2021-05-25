import React, { useEffect } from "react";

import illustration from "./illustration.svg";
import styled from "styled-components";

import { useIsOffline } from "./hooks";

import Button from "@agir/front/genericComponents/Button";
import background from "@agir/front/genericComponents/images/illustration-404.svg";
import style from "@agir/front/genericComponents/_variables.scss";

import TopBar from "@agir/front/allPages/TopBar";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: calc(100vh - 74px);
  margin-top: 74px;
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

const StyledButton = styled(Button)`
  max-width: 450px;
  width: 100%;
  margin-top: 2rem;
  justify-content: center;
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

// Most of the time, if we are in the app on unknow URL, it is because of service worker no network handling
const NotFoundPage = () => {
  const isOffline = useIsOffline();

  // We try to reload every 5 second
  useEffect(() => {
    if (!isOffline) {
      return;
    }

    setTimeout(() => {
      window.location.reload();
    }, 5000);
  }, [isOffline]);

  if (isOffline === null) return null;

  return (
    <PageStyle>
      <TopBar />
      <Container>
        {isOffline ? (
          <OfflineBlock>
            <img src={illustration} style={{ marginBottom: "32px" }} />
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
              Page introuvable
            </h1>
            <span>Cette page n’existe pas ou plus</span>
            <StyledButton color="primary" block as="Link" route="events">
              Retourner à l'accueil
            </StyledButton>
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
export default NotFoundPage;
