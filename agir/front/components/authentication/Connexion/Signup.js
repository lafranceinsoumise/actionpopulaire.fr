import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

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
    > div:nth-child(2) {
      width: 100%;
  }
`;

const defaultData = {
  email: "",
  postalCode: "",
  reasonChecked: 0,
};

const fromGroupEvent = false;

const SignUp = () => {
  const [rgpdChecked, setRgpdChecked] = useState(false);
  const [formData, setFormData] = useState(defaultData);

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

  return (
    <div style={{ width: "500px", maxWidth: "100%", paddingBottom: "1.5rem" }}>
      {!fromGroupEvent ? (
        <h1>Je m'inscris</h1>
      ) : (
        <h1 style={{ fontSize: "26px" }}>
          Je m’inscris pour participer à l’événement
        </h1>
      )}

      <div style={{ display: "inline-block", marginTop: "0.5rem" }}>
        <span>Déjà inscrit·e ?</span>
        &nbsp;
        <span style={{ color: style.primary500, fontWeight: 700 }}>
          Je me connecte
        </span>
      </div>

      {!fromGroupEvent && (
        <>
          <span
            style={{
              display: "inline-block",
              margin: "1.25rem 0",
              fontWeight: 500,
            }}
          >
            Pour quelle campagne rejoignez-vous Action Populaire ?
          </span>

          <ul style={{ padding: "0", listStyleType: "none" }}>
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
          <label htmlFor="">Email</label>
          <TextField
            name="email"
            placeholder="Adresse e-mail"
            onChange={handleChange}
            value={formData.postalCode}
          />
        </div>
        <div>
          <label htmlFor="">Code postal</label>
          <TextField
            name="postalCode"
            placeholder=""
            onChange={handleChange}
            value={formData.phone}
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
        <input type="checkbox" checked={rgpdChecked} onChange={null} />
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
