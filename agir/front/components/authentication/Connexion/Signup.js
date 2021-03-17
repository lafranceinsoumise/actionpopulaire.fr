import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import Link from "@agir/front/app/Link";
import { signUp } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory } from "react-router-dom";
import { BlockSwitchLink } from "./styledComponents";

const InputGroup = styled.div`
  display: inline-flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 1.25rem;
  > div:nth-child(1) {
    width: 340px;
  }
  > div:nth-child(2) {
    width: 140px;
  }

  @media (max-width: ${style.collapse}px) {
    display:block;
    > div:nth-child(1) {
      width: 100%;
    }
`;

const fromGroupEvent = false;

const defaultData = {
  email: "",
  postalCode: "",
  reasonChecked: !fromGroupEvent ? 0 : null,
};

const SignUp = () => {
  const history = useHistory();
  const [rgpdChecked, setRgpdChecked] = useState(false);
  const [formData, setFormData] = useState(defaultData);
  const [error, setError] = useState({});

  const handleRgpdCheck = () => {
    setRgpdChecked(!rgpdChecked);
  };

  const handleReasonChecked = (value) => {
    setFormData({ ...formData, reasonChecked: value });
  };

  const handleChange = (e) => {
    const newFormData = { ...formData };
    newFormData[e.target.name] = e.target.value;
    setFormData(newFormData);
  };

  const handleSubmit = async () => {
    if (!rgpdChecked) {
      console.log("error : NO RGPD Checked");
      return;
    }
    setError({});
    console.log("formData", formData);
    const data = await signUp(formData);
    console.log("data : ", data);
    if (data.error) {
      setError(data.error);
      return;
    }
    const route = routeConfig.codeSignup.getLink();
    history.push(route);
  };

  return (
    <div style={{ width: "500px", maxWidth: "100%", paddingBottom: "1.5rem" }}>
      {!fromGroupEvent ? (
        <h1>Je m'inscris</h1>
      ) : (
        <h1 style={{ fontSize: "26px" }}>
          Je m’inscris pour participer à l’événement
        </h1>
      )}

      <BlockSwitchLink>
        <span>Déjà inscrit·e ?</span>
        &nbsp;
        <span>
          <Link route="login">Je me connecte</Link>
        </span>
      </BlockSwitchLink>

      {!fromGroupEvent && (
        <>
          <span
            style={{
              display: "inline-block",
              margin: "1.25rem 0",
              marginBottom: "10px",
              fontWeight: 600,
              fontSize: "13px",
            }}
          >
            Pour quelle campagne rejoignez-vous Action Populaire ?
          </span>

          <ul style={{ padding: "0", margin: "0", listStyleType: "none" }}>
            <li onClick={() => handleReasonChecked(0)}>
              <label style={{ cursor: "pointer", fontWeight: 400 }}>
                <input
                  type="radio"
                  value="0"
                  onChange={() => {}}
                  checked={0 === formData.reasonChecked}
                />
                <span>&nbsp; La présidentielle de 2022</span>
              </label>
            </li>
            <li onClick={() => handleReasonChecked(1)}>
              <label style={{ cursor: "pointer", fontWeight: 400 }}>
                <input
                  type="radio"
                  value="1"
                  onChange={() => {}}
                  checked={1 === formData.reasonChecked}
                />
                <span>&nbsp; Une autre campagne de la France Insoumise</span>
              </label>
            </li>
          </ul>
        </>
      )}

      <InputGroup>
        <div>
          <TextField
            label="Email"
            name="email"
            error={error && error.email}
            placeholder=""
            onChange={handleChange}
            value={formData.email}
          />
        </div>
        <div>
          <TextField
            label="Code postal"
            name="postalCode"
            error={error && error.postalCode}
            placeholder=""
            onChange={handleChange}
            value={formData.posatalCode}
          />
        </div>
      </InputGroup>

      <div
        onClick={handleRgpdCheck}
        style={{
          marginTop: "1rem",
          marginBottom: "2rem",
          cursor: "pointer",
          userSelect: "none",
        }}
      >
        <input type="checkbox" checked={rgpdChecked} onChange={() => {}} />
        &nbsp;J'accepte que mes informations soient traitées par Action
        Populaire, conformément à la&nbsp;
        <a
          href="https://infos.actionpopulaire.fr/mentions-legales/"
          target="_blank"
        >
          politique de conservation des données
        </a>
      </div>

      <Button
        onClick={handleSubmit}
        color="primary"
        style={{
          marginTop: "0.5rem",
          maxWidth: "100%",
          width: "100%",
          justifyContent: "center",
        }}
      >
        {!fromGroupEvent ? "Créer mon compte" : "Je participe !"}
      </Button>
    </div>
  );
};

export default SignUp;
