import Proptypes from "prop-types";
import React, { useState, useEffect } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import JLM_rounded from "@agir/front/genericComponents/images/JLM_rounded.png";
import LFI_rounded from "@agir/front/genericComponents/images/LFI_rounded.png";
import checkCirclePrimary from "@agir/front/genericComponents/images/check-circle-primary.svg";

import { updateProfile } from "@agir/front/authentication/api";

const RadioLabel = styled.div``;

const Container = styled.div`
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1.5rem;

  @media (max-width: ${style.collapse}px) {
    align-items: stretch;
  }

  h1 {
    font-size: 26px;
    font-weight: 700;
    line-height: 39px;
    text-align: center;
    margin-bottom: 0;
    margin-top: 0;
    max-width: 450px;

    @media (max-width: ${style.collapse}px) {
      font-size: 1.125rem;
      line-height: 1.5;
      text-align: left;
      max-width: 100%;
    }

    span {
      display: block;

      @media (max-width: ${style.collapse}px) {
        display: inline;
      }
    }
  }

  h2 {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0;
    margin-top: 0;
    max-width: 450px;

    @media (max-width: ${style.collapse}px) {
      max-width: 100%;
    }
  }

  p {
    text-align: center;
  }

  ${RadioLabel} {
    margin-top: 0.5rem;
    margin-bottom: 1rem;

    @media (max-width: ${style.collapse}px) {
      text-align: left;
    }
  }

  & > ${Button} {
    width: 356px;
    max-width: 100%;
    margin-top: 2rem;
    justify-content: center;

    @media (max-width: ${style.collapse}px) {
      width: 100%;
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
    max-width: 100%;
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
  padding: 1.5rem;
  position: relative;
  cursor: pointer;
  transition: ease 0.2s;

  @media (max-width: ${style.collapse}px) {
    flex-direction: row;
    justify-content: flex-start;
    width: 100%;
    text-align: left;
  }

  &.responsive-margin {
    @media (max-width: ${style.collapse}px) {
      margin-top: 1rem;
    }
    @media (min-width: ${style.collapse}px) {
      margin-left: 1.5rem;
    }
  }

  ${(props) => {
    if (props.$checked) {
      return `
        border 1px solid ${style.primary500};
        box-shadow: 0px 0px 3px ${style.primary500}, 0px 2px 0px rgba(87, 26, 255, 0.2);
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
    font-size: 1rem;

    @media (max-width: ${style.collapse}px) {
      margin-top: 0;
    }
  }
  img {
    width: 114px;

    @media (max-width: ${style.collapse}px) {
      width: 80px;
    }
  }
`;

const InputRadio = styled.div`
  div {
    width: 1.3rem;
    height: 1.3rem;
    border: 1px solid #000a2c;
    border-radius: 20px;
  }
  img {
    width: 1.3rem;
  }
`;

const [is2022, isInsoumise] = [0, 1];

const notificationList = {
  0: [
    {
      label: "Grands événements de la campagne",
      value: "2022_exceptionnel",
      selected: true,
    },
    {
      label: "Lettres d'informations, environ une fois par semaine",
      value: "2022",
      selected: true,
    },
    {
      label: "Actions en ligne",
      value: "2022_en_ligne",
      selected: false,
    },
    {
      label: "Agir près de chez moi",
      value: "2022_chez_moi",
      selected: false,
    },
    {
      label: "L’actualité sur le programme",
      value: "2022_programme",
      selected: false,
    },
  ],
  1: [
    {
      label: "Recevez des informations sur la France insoumise",
      value: "LFI",
      selected: true,
    },
  ],
};

// return array of newsletter value as string
const filterNewsletter = (newsList) => {
  if (!Array.isArray(newsList)) {
    return [];
  }
  const res = newsList
    .map((e) => {
      if (e.selected) return e.value;
    })
    .filter((e) => {
      if (e !== undefined) return e;
    });
  return res;
};

const ChooseCampaign = ({ dismiss }) => {
  const [notifs, setNotifs] = useState(null);
  const [reasonChecked, setReasonChecked] = useState();
  const [newsLetters, setNewsletters] = useState([]);
  const [submitted, setSubmitted] = useState(false);

  const fromSignup = true;

  const handleReasonChecked = (value) => {
    setReasonChecked(value);
    setNotifs(notificationList[value]);
    setNewsletters(filterNewsletter(notifs));
  };

  const handleToggleNotif = (index) => {
    const newNotifs = [...notifs];
    newNotifs[index].selected = !newNotifs[index].selected;
    setNotifs(newNotifs);
    setNewsletters(filterNewsletter(newNotifs));
  };

  const handleSubmit = async () => {
    setSubmitted(true);
    await updateProfile({
      reasonChecked: reasonChecked,
      newsletter: newsLetters,
    });
    setSubmitted(false);
    dismiss();
  };

  useEffect(() => {
    setNewsletters(filterNewsletter(notifs));
  }, [notifs]);

  return (
    <Container>
      {fromSignup && (
        <div
          style={{
            display: "inline-flex",
            fontWeight: 600,
            padding: "0.5rem 1rem",
            backgroundColor: style.green100,
            marginBottom: "2rem",
            flex: "0 0 auto",
            alignSelf: "center",
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

      <h1>
        <span>Pour quelle campagne</span>{" "}
        <span>rejoignez-vous Action Populaire&nbsp;?</span>
      </h1>
      <RadioLabel>
        Nous vous suggérerons des actions qui vous intéressent
      </RadioLabel>

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
              <div />
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
              <div />
            )}
          </InputRadio>
        </RadioBlock>
      </ContainerRadio>

      <div style={{ textAlign: "left", marginTop: "1.5rem" }}>
        {is2022 === reasonChecked && (
          <h2 style={{ textAlign: "left", marginBottom: "0.5rem" }}>
            Recevez des informations sur la campagne
          </h2>
        )}
        {Array.isArray(notifs) &&
          notifs.map((notif) => (
            <CheckboxField
              key={notif.value}
              name={notif.value}
              label={notif.label}
              value={notif.selected}
              onChange={() => handleToggleNotif(notif)}
            />
          ))}
      </div>

      <Button color="primary" onClick={handleSubmit} disabled={submitted}>
        Continuer
      </Button>
    </Container>
  );
};
ChooseCampaign.propTypes = {
  dismiss: Proptypes.func.isRequired,
};
export default ChooseCampaign;
