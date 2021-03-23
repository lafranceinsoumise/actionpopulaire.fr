import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import JLM_rounded from "@agir/front/genericComponents/images/JLM_rounded.png";
import LFI_rounded from "@agir/front/genericComponents/images/LFI_rounded.png";
import checkCirclePrimary from "@agir/front/genericComponents/images/check-circle-primary.svg";
import { updateProfile } from "../../api";

const Container = styled.div`
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 24px;

  h1 {
    font-size: 26px;
    font-weight: 700,
    line-height: 39px;
    text-align: center;
    margin-bottom: 0px;
    margin-top: 16px;
    max-width: 450px;
  }
  p {
    text-align: center;
  }
  @media (max-width: ${style.collapse}px) {
    h1 {
      font-size: 18px;
    }
  }
`;

const ContainerRadio = styled.div`
  display: flex;
  max-width: 525px;
  width: 100%;
  user-select: none;
  @media (max-width: ${style.collapse}px) {
    flex-direction: column;
  }
`;

const RadioBlock = styled.div`
  width: 250px;
  display: flex;
  flex-align: center;
  text-align: center;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 24px;
  margin-top: 38px;
  position: relative;
  cursor: pointer;
  transition: ease 0.2s;

  @media (max-width: ${style.collapse}px) {
    flex-direction: row;
    width: 100%;
  }
  &.responsive-margin {
    @media (max-width: ${style.collapse}px) {
      margin-top: 16px;
    }
    @media (min-width: ${style.collapse}px) {
      margin-left: 24px;
    }
  }

  ${(props) => {
    if (props.$checked) {
      return `
        border 2px solid ${style.primary500};
        box-shadow: 0px 0px 3px #571AFF, 0px 2px 0px rgba(87, 26, 255, 0.2);
        `;
    } else {
      return `
        border: 1px solid #C4C4C4;
      `;
    }
  }};

  &:hover {
    border-color: ${style.primary500};
  }

  > div {
    position: absolute;
    right: 12px;
    top: 12px;
    margin: 0px;
  }
  input {
    position: absolute;
    right: 12px;
    top: 12px;
    margin: 0px;
    border: 1px solid #333;
  }
  span {
    ${(props) => props.$checked && `color: ${style.primary500}`};
    margin-top: 14px;
    padding: 10px;
    font-weight: 600;
    font-size: 16px;
  }
  img {
    width: 114px;
  }
`;

const InputRadio = styled.div`
  div {
    width: 16px;
    height: 16px;
    border: 1px solid #000a2c;
    border-radius: 20px;
  }
  img {
    width: 16px;
  }
`;

const [is2022, isInsoumise] = [0, 1];

const notificationList = {
  0: [
    {
      label: "Les lettres d'informations, environ une fois par semaine",
      value: "newsHebdo",
      selected: true,
    },
    {
      label: "Actions en ligne",
      value: "actOnline",
      selected: false,
    },
    {
      label: "Agir près de chez moi",
      value: "nearMe",
      selected: false,
    },
    {
      label: "L’actualité sur le programme",
      value: "newsProgram",
      selected: false,
    },
  ],
  1: [
    {
      label: "Recevez des informations sur la France insoumise",
      value: "newsInsoumises",
      selected: true,
    },
  ],
};

const ChooseCampaign = ({ dismiss }) => {
  const [reasonChecked, setReasonChecked] = useState(0);
  const [notifs, setNotifs] = useState(notificationList[is2022]);
  const [submitted, setSubmitted] = useState(false);
  const fromSignup = true;

  const handleReasonChecked = (value) => {
    setReasonChecked(value);
    setNotifs(notificationList[value]);
  };

  const handleToggleNotif = (index) => {
    const newNotifs = [...notifs];
    newNotifs[index].selected = !newNotifs[index].selected;
    setNotifs(newNotifs);
  };

  const handleSubmit = async () => {
    setSubmitted(true);
    await updateProfile({ reasonChecked: reasonChecked });
    setSubmitted(false);
    dismiss();
  };

  return (
    <Container>
      {fromSignup && (
        <div
          style={{
            display: "inline-flex",
            fontWeight: 600,
            padding: "0.5rem 1rem",
            backgroundColor: style.green100,
          }}
        >
          <FeatherIcon
            name="check"
            color="green"
            strokeWidth={4}
            width="1rem"
            style={{ marginRight: "12px" }}
          />
          Votre compte a été créé
        </div>
      )}

      <h1>Pour quelle campagne rejoignez-vous Action Populaire ?</h1>
      <div style={{ marginTop: "2rem" }}>
        Nous vous suggérerons des actions qui vous intéressent
      </div>

      <ContainerRadio>
        <RadioBlock
          onClick={() => handleReasonChecked(0)}
          $checked={is2022 === reasonChecked}
        >
          <img src={JLM_rounded} alt="Jean-Luc Mélenchon" />
          <span>La campagne présidentielle 2022</span>
          <InputRadio>
            {is2022 === reasonChecked ? (
              <img src={checkCirclePrimary} alt="" />
            ) : (
              <div></div>
            )}
          </InputRadio>
        </RadioBlock>
        <RadioBlock
          onClick={() => handleReasonChecked(1)}
          $checked={isInsoumise === reasonChecked}
          className="responsive-margin"
        >
          <img src={LFI_rounded} alt="La France Insoumise" />
          <span>Une autre campagne de la France Insoumise</span>
          <InputRadio>
            {isInsoumise === reasonChecked ? (
              <img src={checkCirclePrimary} alt="" />
            ) : (
              <div></div>
            )}
          </InputRadio>
        </RadioBlock>
      </ContainerRadio>

      <div style={{ textAlign: "left", marginTop: "1rem" }}>
        {notifs.map((e, id) => (
          <CheckboxField
            key={id}
            name={e.value}
            label={e.label}
            value={e.selected}
            onChange={() => handleToggleNotif(id)}
          />
        ))}
      </div>

      <Button
        color="primary"
        onClick={handleSubmit}
        disabled={submitted}
        style={{
          width: "356px",
          maxWidth: "100%",
          marginTop: "2rem",
          justifyContent: "center",
        }}
      >
        Continuer
      </Button>
    </Container>
  );
};

export default ChooseCampaign;
