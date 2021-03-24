import React, { useState, useEffect } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import SelectField from "@agir/front/formComponents/SelectField";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import helloDesktop from "@agir/front/genericComponents/images/hello-desktop.svg";
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

const optional = <span style={{ fontWeight: 400 }}>(facultatif)</span>;
const defaultData = {
  displayName: "",
  firstName: "",
  lastName: "",
  phone: "",
  postalCode: "",
  mandates: [],
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
  const [error, setError] = useState({});
  const [showMandate, setShowMandate] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [mandat, setMandat] = useState(mandatList[0]);

  const getProfileInfos = async () => {
    const { data } = await getProfile();

    setFormData({
      displayName: data.displayName,
      firstName: data.firstName,
      lastName: data.lastName,
      phone: data.contactPhone,
      postalCode: data.zip,
      mandates: data.mandates,
    });
    setShowMandate(data.mandates?.length > 0);
  };

  useEffect(() => {
    getProfileInfos();
  }, []);

  const handleInputChange = (e) => {
    const newFormData = { ...formData };
    newFormData[e.target.name] = e.target.value;
    setFormData(newFormData);
  };

  const toggleShowMandate = () => setShowMandate(!showMandate);

  const handleMandateChange = (e) => {
    setMandat(e);
    setFormData({ ...formData, mandates: [e.value] });
  };

  const handleSubmit = async () => {
    setSubmitted(true);
    setError({});
    const data = await updateProfile(formData);
    setSubmitted(false);
    if (data.error) {
      setError(data.error);
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
            Le nom que tout le monde pourra voir. Indiquez par exemple votre
            prénom ou un pseudonyme.
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
          <InputCheckbox onClick={toggleShowMandate}>
            <input
              type="checkbox"
              name="mandat"
              checked={showMandate}
              onChange={() => {}}
            />
            <span style={{ fontSize: "16px" }}>&nbsp; J'ai un mandat</span>
          </InputCheckbox>
          {showMandate && (
            <div style={{ marginTop: "10px" }}>
              <SelectField
                label="Mandat"
                name="mandat"
                placeholder=""
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
