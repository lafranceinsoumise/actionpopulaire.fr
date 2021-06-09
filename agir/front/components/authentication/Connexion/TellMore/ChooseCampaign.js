import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import JLM_rounded from "@agir/front/genericComponents/images/JLM_rounded.png";
import LFI_rounded from "@agir/front/genericComponents/images/LFI_rounded.png";
import checkCirclePrimary from "@agir/front/genericComponents/images/check-circle-primary.svg";

import { updateProfile } from "@agir/front/authentication/api";

const RadioLabel = styled.div``;

const Container = styled.form`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 3rem 1.5rem 1.5rem;

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
    padding-top: 1rem;
    padding-bottom: 2rem;

    @media (max-width: ${style.collapse}px) {
      padding-top: 0.5rem;
      padding-bottom: 1rem;
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

const NEWSLETTER_OPTIONS = {
  is2022: [
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
  isInsoumise: [
    {
      label: "Recevez des informations sur la France insoumise",
      value: "LFI",
      selected: true,
    },
  ],
};

const CampaignOption = (props) => {
  const { value, img, label, selected, onChange } = props;

  const handleChange = useCallback(() => {
    onChange && onChange(value);
  }, [value, onChange]);
  return (
    <RadioBlock onClick={handleChange} $checked={selected}>
      <img src={img} width="114" height="114" alt="Jean-Luc Mélenchon" />
      <span>{label}</span>
      <InputRadio>
        {selected ? (
          <img src={checkCirclePrimary} width="16" height="16" />
        ) : (
          <div />
        )}
      </InputRadio>
    </RadioBlock>
  );
};
CampaignOption.propTypes = {
  value: PropTypes.string,
  label: PropTypes.string,
  img: PropTypes.string,
  selected: PropTypes.bool,
  onChange: PropTypes.func,
};

const NewsletterOption = (props) => {
  const { value, label, selected, onChange } = props;

  const handleChange = useCallback(
    (e) => {
      onChange && onChange(value, e.target.checked);
    },
    [value, onChange]
  );

  return (
    <CheckboxField
      name={value}
      label={label}
      value={selected}
      onChange={handleChange}
    />
  );
};
NewsletterOption.propTypes = {
  value: PropTypes.string,
  label: PropTypes.string,
  selected: PropTypes.bool,
  onChange: PropTypes.func,
};

const ChooseCampaign = ({ dismiss }) => {
  const [campaign, setCampaign] = useState();
  const [newsletters, setNewsletters] = useState([]);
  const [submitted, setSubmitted] = useState(false);

  const fromSignup = true;

  const handleCampaignChange = useCallback((value) => {
    setCampaign(value);
  }, []);

  const handleChangeNewsletter = useCallback((value, checked) => {
    if (checked) {
      setNewsletters((state) => [...state, value]);
    } else {
      setNewsletters((state) => state.filter((item) => item !== value));
    }
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setSubmitted(true);
      await updateProfile({
        is2022: campaign === "is2022",
        isInsoumise: campaign === "isInsoumise",
        newsletters,
      });
      await dismiss();
      setSubmitted(false);
    },
    [campaign, dismiss, newsletters]
  );

  useEffect(() => {
    if (!campaign || !NEWSLETTER_OPTIONS[campaign]) {
      setNewsletters([]);
      return;
    }
    setNewsletters(
      NEWSLETTER_OPTIONS[campaign]
        .filter((option) => option.selected)
        .map((option) => option.value)
    );
  }, [campaign]);

  return (
    <div>
      <Hide under>
        <div style={{ position: "fixed" }}>
          <Link route="events">
            <LogoAP
              style={{ marginTop: "2rem", paddingLeft: "2rem", width: "200px" }}
            />
          </Link>
        </div>
      </Hide>
      <Container onSubmit={handleSubmit}>
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
          <CampaignOption
            onChange={handleCampaignChange}
            value="is2022"
            selected={campaign === "is2022"}
            img={JLM_rounded}
            label="La campagne présidentielle 2022"
          />
          <Spacer size="1rem" />
          <CampaignOption
            onChange={handleCampaignChange}
            value="isInsoumise"
            selected={campaign === "isInsoumise"}
            img={LFI_rounded}
            label="Une autre campagne de la France Insoumise"
          />
        </ContainerRadio>

        <div style={{ textAlign: "left", marginTop: "1.5rem" }}>
          {campaign === "is2022" && (
            <h2 style={{ textAlign: "left", marginBottom: "0.5rem" }}>
              Recevez des informations sur la campagne
            </h2>
          )}
          {campaign &&
            Array.isArray(NEWSLETTER_OPTIONS[campaign]) &&
            NEWSLETTER_OPTIONS[campaign].map((option) => (
              <NewsletterOption
                key={option.value}
                {...option}
                selected={newsletters.includes(option.value)}
                onChange={handleChangeNewsletter}
              />
            ))}
        </div>

        <Button color="primary" type="submit" disabled={!campaign || submitted}>
          Continuer
        </Button>
      </Container>
    </div>
  );
};
ChooseCampaign.propTypes = {
  dismiss: PropTypes.func.isRequired,
};
export default ChooseCampaign;
