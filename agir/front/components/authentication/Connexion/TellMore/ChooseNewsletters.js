import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import checkCirclePrimary from "@agir/front/genericComponents/images/check-circle-primary.svg";

import { updateProfile } from "@agir/front/authentication/api";
import { getNewsletterOptions } from "@agir/front/authentication/common";

const Container = styled.form`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 7rem 2rem 1.5rem;
  width: 100%;
  max-width: 640px;
  margin: 0 auto;

  @media (max-width: ${style.collapse}px) {
    max-width: 400px;
    padding: 3rem 2rem 1.5rem;
    text-align: left;
  }

  h2,
  p {
    margin: 0;
    max-width: 100%;
  }

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    line-height: 1.5;

    @media (max-width: ${style.collapse}px) {
      font-size: 1.125rem;
    }

    span {
      display: block;
    }
  }

  & > ${Button} {
    width: 100%;
    max-width: 356px;

    &[type="button"] {
      background-color: transparent;
      color: ${style.black500};
      font-size: 0.875rem;
      font-weight: 400;
    }
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
    [value, onChange],
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

const ChooseNewsletters = ({ user, dismiss }) => {
  const [newsletters, setNewsletters] = useState(undefined);
  const [submitted, setSubmitted] = useState(false);

  const newsletterOptions = useMemo(() => getNewsletterOptions(user), [user]);

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
      await updateProfile({ newsletters });
      await dismiss();
      setSubmitted(false);
    },
    [dismiss, newsletters],
  );

  useEffect(() => {
    if (!user) {
      return;
    }

    if (user.newsletters.length > 0) {
      return setNewsletters(user.newsletters);
    }

    setNewsletters(
      newsletterOptions
        .filter((option) => option.selected)
        .map((option) => option.value),
    );
  }, [user, newsletterOptions]);

  return (
    <div>
      <Hide $under>
        <div style={{ position: "fixed" }}>
          <Link route="events">
            <LogoAP
              style={{ marginTop: "2rem", paddingLeft: "2rem", width: "200px" }}
            />
          </Link>
        </div>
      </Hide>
      <Container onSubmit={handleSubmit}>
        <h2>Recevez l'actualité de la France insoumise</h2>
        <Spacer size="1rem" />
        <p>
          Choisissez parmi la liste ci-dessous les lettres d'information du
          mouvement auxquelles vous souhaitez vous abonner
        </p>
        <Spacer size="2rem" />
        <div style={{ textAlign: "left" }}>
          {newsletterOptions.map((option) => (
            <NewsletterOption
              key={option.value}
              {...option}
              selected={newsletters && newsletters.includes(option.value)}
              onChange={handleChangeNewsletter}
            />
          ))}
        </div>
        <Spacer size="2rem" />
        <Button color="primary" type="submit" disabled={submitted}>
          Continuer
        </Button>
        <Spacer size="1rem" />
        <Button type="button" onClick={dismiss} disabled={submitted}>
          Passer cette étape
        </Button>
      </Container>
    </div>
  );
};
ChooseNewsletters.propTypes = {
  dismiss: PropTypes.func.isRequired,
  user: PropTypes.object,
};
export default ChooseNewsletters;
