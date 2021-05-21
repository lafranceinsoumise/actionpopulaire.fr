import React from "react";
import Button from "@agir/front/genericComponents/Button";

import background from "@agir/front/genericComponents/images/illustration-404.svg";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { routeConfig } from "@agir/front/app/routes.config";

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

export const NotFoundPage = () => {
  return (
    <>
      <TopBar />
      <Container>
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
      </Container>
    </>
  );
};

export default NotFoundPage;
