import React, { useState, useEffect } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
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

const SelectField = styled.select`
  display: block;
  width: 100%;
  height: 36px;
  padding: 6px 12px;
  font-size: 16px;
  line-height: 1.428571429;
  color: #555555;
  background-color: #fff;
  background-image: none;
  border: 1px solid #ccc;
  border-radius: 0px;
  -webkit-box-shadow: inset 0 1px 1px rgb(0 0 0 / 8%);
  box-shadow: inset 0 1px 1px rgb(0 0 0 / 8%);
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
    name: "Maire",
    value: "maire",
  },
  {
    name: "Autre mandat municipal",
    value: "municipal",
  },
  {
    name: "Mandat départemental",
    value: "departemental",
  },
  {
    name: "Mandat régional",
    value: "regional",
  },
];

const TellMore = ({ dismiss }) => {
  const [formData, setFormData] = useState(defaultData);
  const [error, setError] = useState({});
  const [showMandate, setShowMandate] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [firstMandate, setFirstMandate] = useState("");

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
    if (data.mandates?.length) setFirstMandate(data.mandates[0]);
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
    setFormData({ ...formData, mandates: [e.target.value] });
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
              <label>Mandat</label>
              <SelectField onChange={handleMandateChange}>
                {mandatList.map((elt, id) => (
                  <option
                    key={id}
                    value={elt.name}
                    selected={elt.value === firstMandate}
                  >
                    {elt.name}
                  </option>
                ))}
              </SelectField>
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
