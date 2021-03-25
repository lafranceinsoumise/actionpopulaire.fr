import React, { useCallback, useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import actImage from "@agir/front/app/Homepage/images/act.jpg";
import meetImage from "@agir/front/app/Homepage/images/meet.jpg";
import organizeImage from "@agir/front/app/Homepage/images/organize.jpg";
import logo from "@agir/front/genericComponents/images/logoActionPopulaire.png";

const Mark = styled.span`
  width: 1.5rem;
  height: 0.25rem;
  margin: 0.188rem;
  display: inline-block;
  transition: ease 0.2s;
  background-color: ${(props) =>
    props.$active ? style.primary500 : style.black200};
`;

const Block = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  text-align: center;
  height: 100vh;
  justify-content: space-between;

  & > div:nth-child(2) {
    max-width: 100%;
    padding-left: 2rem;
    padding-right: 2rem;
  }
`;

const BlockConnexion = styled.div`
  display: flex;
  flex-direction: column;
  justify: center;
  align-items: center;
  height: 100vh;
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-align: center;
  flex-direction: column;
  width: 100%;
  align-items: center;
  padding: 2rem;
`;

const BackgroundTriangle = styled.div`
  width: 100%;
  background-color: ${style.secondary500};
  margin-top: -1px;
  div {
    background-color: white;
    height: 80px;
    margin-bottom: -1px;
    clip-path: polygon(0px 100%, 100% 0px, 100% 100%, 0px 100%);
  }
`;

const WhiteTriangle = styled.div`
  width: 100%;
<<<<<<< HEAD
  background-color: ${style.primary500};
  margin-top: -1px;
  flex-basis: 120px;
  flex-grow: 1;

  display: flex;
  flex-direction: column;

  div:nth-child(1) {
    flex-grow: 1;
  }

  div:nth-child(2) {
=======
  height: 190px;
  div {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
>>>>>>> 5bfe04df... styles: new design introApp
    background-color: white;
    height: 80px;
    clip-path: polygon(0px 100%, 100% 0px, 100% 100%, 0px 100%);
  }
`;

const HeaderImage = styled.div`
  background-size: cover;
  background-position: cover;
  position: relative;
  flex-basis: 90px;
  flex-shrink: 1;
  flex-grow: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;

  img {
    width: 90%;
    max-width: 330px;
    position: absolute;
    bottom: 0;
  }
`;

const IntroDescriptionContainer = styled.div`
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
`;

const DescriptionContainer = styled.div`
  background-color: ${style.secondary500};
  padding: 1.4rem;
  width: 100%;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  position: relative;
  text-align: center;
  flex-grow: 1;
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const StyledButton = styled(Button)`
  max-width: 100%;
  width: 330px;
  height: 70px;
  font-size: 20px;
  justify-content: center;
  margin-top: 2.5rem;
`;

const items = [
  {
    name: "Rencontrez",
    description: (
      <>
        d'autres membres et&nbsp;<InlineBlock>agissez ensemble !</InlineBlock>
      </>
    ),
    image: meetImage,
  },
  {
    name: "Agissez concrètement",
    description: (
      <>
        participez aux action, diffusez notre programme et commandez&nbsp;
        <InlineBlock>du matériel</InlineBlock>
      </>
    ),
    image: actImage,
  },
  {
    name: "Organisez et rejoignez",
    description: (
      <>
        une équipe de soutien&nbsp;<InlineBlock>autour de vous !</InlineBlock>
      </>
    ),
    image: organizeImage,
  },
];

const IntroApp = () => {
  const [index, setIndex] = useState(0);

  const showConnexion = index >= items.length;

  const handleClick = useCallback(() => {
    setIndex((index) => index + 1);
  }, []);

  return (
    <>
      {!showConnexion && (
        <Block>
          <HeaderImage
            style={{ backgroundImage: `url(${items[index].image})` }}
          >
            <WhiteTriangle>
              <div></div>
            </WhiteTriangle>
          </HeaderImage>

          <div style={{ paddingTop: "0.5rem" }}>
            <p
              style={{
                color: style.primary500,
                fontWeight: 700,
                fontSize: "1.75rem",
              }}
            >
              {items[index].name}
            </p>

            <p style={{ fontSize: "1.2rem", marginTop: "0.375rem" }}>
              {items[index].description}
            </p>

            <StyledButton color="secondary" onClick={handleClick}>
              Continuer
            </StyledButton>

            <div style={{ marginTop: "2rem", marginBottom: "1.5rem" }}>
              <Mark $active={0 === index} />
              <Mark $active={1 === index} />
              <Mark $active={2 === index} />
            </div>
          </IntroDescriptionContainer>
        </Block>
      )}
      {showConnexion && (
        <BlockConnexion>
          <DescriptionContainer>
            <div>
              <img
                src={logo}
                alt=""
                style={{ maxWidth: "300px", marginTop: "2rem" }}
              />
            </div>
          </DescriptionContainer>

          <BackgroundTriangle>
            <div />
          </BackgroundTriangle>

          <ButtonContainer>
            <StyledButton color="primary" as="Link" route="signup">
              Je crée mon compte
            </StyledButton>
            <StyledButton
              color="secondary"
              style={{ marginTop: "0.5rem", marginLeft: "0px" }}
              as="Link"
              route="login"
            >
              Je me connecte
            </StyledButton>
          </ButtonContainer>
        </BlockConnexion>
      )}
    </>
  );
};

export default IntroApp;
