import React, { useState, useEffect } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import SelectField from "@agir/front/formComponents/SelectField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import helloDesktop from "@agir/front/genericComponents/images/hello-desktop.svg";
import { Hide } from "@agir/front/genericComponents/grid";
import { updateProfile, getProfile } from "@agir/front/authentication/api";

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
  min-height: 100vh;
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
    align-items: center;
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

const optional = <span style={{ fontWeight: 400 }}>(facultatif)</span>;
const defaultData = {
  displayName: "",
  firstName: "",
  lastName: "",
  phone: "",
  postalCode: "",
  mandat: [],
};
const mandatList = [
  {
    label: "Maire",
    value: "maire",
  },
  {
    label: "Autre mandat municipal",
    value: "municipal",
  },
  {
    label: "Mandat départemental",
    value: "departemental",
  },
  {
    label: "Mandat régional",
    value: "regional",
  },
];

const TellMore = ({ dismiss }) => {
  const [formData, setFormData] = useState(defaultData);
  const [showMandat, setShowMandat] = useState(false);
  const [mandat, setMandat] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState({});

  const getProfileInfos = async () => {
    const { data } = await getProfile();

    setFormData({
      displayName: data.displayName,
      firstName: data.firstName,
      lastName: data.lastName,
      phone: data.contactPhone,
      postalCode: data.zip,
      mandat: data.mandat,
    });
    if (data.mandat?.length > 0) {
      setShowMandat(true);
      setMandat(mandatList[0]);
    }
  };

  useEffect(() => {
    getProfileInfos();
  }, []);

  const handleInputChange = (e) => {
    const newFormData = { ...formData };
    newFormData[e.target.name] = e.target.value;
    setFormData(newFormData);
  };

  const toggleShowMandat = () => {
    const isMandat = !showMandat;
    setShowMandat(isMandat);
    if (isMandat) {
      setMandat(mandatList[0]);
      return;
    }
    setMandat([]);
  };

  const handleMandateChange = (e) => {
    setMandat(e);
    setFormData({ ...formData, mandat: [e.value] });
  };

  const handleSubmit = async () => {
    setSubmitted(true);
    setError(null);
    const data = await updateProfile(formData);
    if (data.error) {
      setError(data.error);
      setSubmitted(false);
      return;
    }
    dismiss();
  };

  return (
    <div style={{ display: "flex" }}>
      <LeftBlock>
        <img
          src={helloDesktop}
          alt="Bienvenue"
          style={{ width: "220px", paddingRight: "60px" }}
        />
      </LeftBlock>
      <MainBlock>
        <div style={{ width: "100%", maxWidth: "517px" }}>
          <h1>J’en dis plus sur moi</h1>
          <label style={{ marginBottom: "0" }}>Nom public</label> (obligatoire)
          <br />
          <span>
            Le nom que pourrons voir les membres avec qui vous intéragissez.
            Indiquez par exemple votre prénom ou un pseudonyme.
          </span>
          <TextField
            error={error && error.displayName}
            name="displayName"
            placeholder="Exemple : Marie R."
            onChange={handleInputChange}
            value={formData.displayName}
          />
          <TextField
            label={<>Prénom {optional}</>}
            name="firstName"
            placeholder=""
            onChange={handleInputChange}
            value={formData.firstName}
          />
          <TextField
            label={<>Nom {optional}</>}
            id="lastName"
            name="lastName"
            placeholder=""
            onChange={handleInputChange}
            value={formData.lastName}
          />
          <InputGroup>
            <div>
              <TextField
                label="Code postal"
                id="postalCode"
                error={error && error.zip}
                name="postalCode"
                placeholder=""
                onChange={handleInputChange}
                value={formData.postalCode}
              />
            </div>
            <div>
              <TextField
                label={<>Numéro de téléphone {optional}</>}
                id="phone"
                error={error && error.phone}
                name="phone"
                onChange={handleInputChange}
                value={formData.phone}
              />
            </div>
          </InputGroup>
          <div style={{ marginTop: "0.625rem" }}>
            <CheckboxField
              name="mandat"
              label="Je suis élu·e"
              value={showMandat}
              onChange={toggleShowMandat}
            />
          </div>
          {showMandat && (
            <div style={{ marginTop: "10px" }}>
              <SelectField
                label="Mandat"
                name="mandat"
                value={mandat}
                options={mandatList}
                onChange={handleMandateChange}
              />
            </div>
          )}
          <Button
            color="primary"
            onClick={handleSubmit}
            disabled={submitted}
            style={{
              width: "356px",
              maxWidth: "100%",
              marginTop: "1rem",
              marginBottom: "2rem",
              justifyContent: "center",
            }}
          >
            Enregistrer
          </Button>
          {!showMandat && <Hide under style={{ paddingBottom: "79px" }}></Hide>}
        </div>
      </MainBlock>
    </div>
  );
};

export default TellMore;
