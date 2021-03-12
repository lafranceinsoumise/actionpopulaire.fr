import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import styled from "styled-components";

const Container = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;

  h1 {
    font-size: 28px;
    font-weight: 700,
    line-height: 39px;
    text-align: center;
    margin-bottom: 0px;
    margin-top: 16px;
  }
  p {
    text-align: center;
  }
`;

const Form = styled.div`
  box-sizing: border-box;
  margin: 0 auto;
  margin-top: 36px;
  display: flex;
`;

const CodeConnexionDesktop = () => {
  const [code, setCode] = useState("");

  const handleCode = (e) => {
    setCode(e.target.value);
  };

  return (
    <Container>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>
        Votre code de connexion <br />
        vous a été envoyé par e-mail
      </h1>
      <p style={{ marginTop: "32px" }}>
        Entrez le code de connexion que nous avons envoyé à{" "}
        <strong>danielle@simonnet.fr</strong>
      </p>
      <p style={{ marginBottom: "0px" }}>
        Si l’adresse e-mail n’est pas reconnue, il vous sera proposé de vous
        inscrire.
      </p>

      <Form>
        <TextField
          error=""
          id="field"
          label="Code de connexion"
          placeholder=""
          style={{ fontWeight: 600 }}
          onChange={handleCode}
          value={code}
        />
        <div>
          <Button
            color="primary"
            style={{
              marginTop: "24px",
              marginLeft: "10px",
              width: "140px",
              height: "41px",
              justifyContent: "center",
            }}
          >
            Valider
          </Button>
        </div>
      </Form>
    </Container>
  );
};

const CodeConnexion = () => {
  return (
    <>
      <ResponsiveLayout
        MobileLayout={CodeConnexionDesktop}
        DesktopLayout={CodeConnexionDesktop}
      ></ResponsiveLayout>
    </>
  );
};

export default CodeConnexion;
