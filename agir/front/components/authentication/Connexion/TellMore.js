import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import helloDesktop from "@agir/front/genericComponents/images/hello-desktop.svg";

const LeftBlock = styled.div`
  width: 40%;
  height: 100vh;
  display: flex;
  position: relative;
  align-items: center;
  justify-content: flex-end;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const MainBlock = styled.div`
  width: 60%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  font-size: 13px;
  padding: 32px;

  input {
    border-color: #c4c4c4;
  }
  label {
    font-weight: 600;
  }

  h1 {
    margin: 0px;
    margin-bottom: 1.125rem;
    font-weight: 700;
    font-size: 2rem;
  }

  @media (max-width: ${style.collapse}px) {
    width: 100%;
  }
`;

const InputGroup = styled.div`
  display: inline-flex;
  justify-content: space-between;
  width: 100%;
  > div:nth-child(1) {
    width: 155px;
  }
  > div:nth-child(2) {
    width: 346px;
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

const InputCheckbox = styled.div`
  display: flex;
  cursor: pointer;
  user-select: none;
  margin-top: 0.625rem;
`;

const TellMore = () => {
  const [formData, setFormData] = useState({});
  const [hasMandate, setHasMandate] = useState(false);

  const handleInputChange = (e) => {
    const newFormData = { ...formData };
    newFormData[e.target.name] = e.target.value;
    setFormData(newFormData);
  };

  const handleHasMandate = () => {
    setHasMandate(!hasMandate);
  };

  const handleSubmit = () => {
    console.log("formData : ", formData);
  };

  return (
    <div style={{ display: "flex" }}>
      <LeftBlock>
        <img
          src={helloDesktop}
          alt=""
          style={{ width: "220px", paddingRight: "60px" }}
        />
      </LeftBlock>
      <MainBlock>
        <div style={{ width: "100%", maxWidth: "517px" }}>
          <h1>J’en dis plus sur moi</h1>
          <label htmlFor="">Nom public</label> (obligatoire)
          <br />
          <span>
            Le nom que tout le monde pourra voir. Indiquez par exemple votre
            prénom ou un pseudonyme.
          </span>
          <TextField
            error=""
            name="name"
            placeholder="Exemple : Marie R."
            onChange={handleInputChange}
            value={formData.name}
          />
          <label htmlFor="">Prénom</label> (facultatif)
          <TextField
            error=""
            name="firstName"
            placeholder=""
            onChange={handleInputChange}
            value={formData.firstName}
          />
          <label htmlFor="">Nom</label> (facultatif)
          <TextField
            error=""
            name="lastName"
            placeholder=""
            onChange={handleInputChange}
            value={formData.lastName}
          />
          <InputGroup>
            <div>
              <label htmlFor="">Code postal</label>
              <TextField
                error=""
                name="postalCode"
                placeholder=""
                onChange={handleInputChange}
                value={formData.postalCode}
              />
            </div>
            <div>
              <label htmlFor="">Numéro de téléphone</label> (facultatif)
              <TextField
                error=""
                name="phone"
                placeholder=""
                onChange={handleInputChange}
                value={formData.phone}
              />
            </div>
          </InputGroup>
          <InputCheckbox onClick={handleHasMandate}>
            <input type="checkbox" name="mandat" checked={hasMandate} />
            <span style={{ fontSize: "16px" }}>&nbsp; J'ai un mandat</span>
          </InputCheckbox>
          <Button
            color="primary"
            onClick={handleSubmit}
            style={{
              width: "356px",
              maxWidth: "100%",
              marginTop: "1rem",
              justifyContent: "center",
            }}
          >
            Enregistrer
          </Button>
        </div>
      </MainBlock>
    </div>
  );
};

export default TellMore;
