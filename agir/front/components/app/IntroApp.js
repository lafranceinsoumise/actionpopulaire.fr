import React, { useState, useCallback } from "react";
import Button from "@agir/front/genericComponents/Button";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import img1 from "@agir/front/genericComponents/images/introApp1.jpg";
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
  max-width: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  border: 1px solid #ddd;
  text-align: center;
  overflow: auto;
  max-height: 100%;
  height: 100vh;
`;

const BlockConnexion = styled.div`
  display: flex;
  flex-direction: column;
  justify: center;
  align-items: center;
`;

const ButtonContainer = styled.div`
  margin-bottom: 40px;
  display: flex;
  flex-align: center;
  flex-direction: column;
`;

const BackgroundTriangle = styled.div`
  width: 100%;
  background-color: ${style.secondary500};
  div {
    background-color: white;
    height: 100px;
    clip-path: polygon(0px 100%, 100% 0px, 100% 100%, 0px 100%);
  }
`;

const DescriptionContainer = styled.div`
  background-color: ${style.secondary500};
  padding: 1.4rem;
  // height: 618px;
  min-height: 375px;
  width: 100%;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  position: relative;
  text-align: center;
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const items = [
  {
    name: "Rencontrez",
    description: (
      <>
        d'autres membres et&nbsp;<InlineBlock>agissez ensemble !</InlineBlock>
      </>
    ),
    image: img1,
  },
  {
    name: "Agissez concrètement",
    description: (
      <>
        formez-vous et commandez du matériel, tracts&nbsp;
        <InlineBlock>et affiches !</InlineBlock>
      </>
    ),
    image: img1,
  },
  {
    name: "Organisez et rejoignez",
    description: (
      <>
        une équipe de soutien&nbsp;<InlineBlock>autour de vous !</InlineBlock>
      </>
    ),
    image: img1,
  },
];

const IntroApp = () => {
  const [index, setIndex] = useState(0);

  const showConnexion = index >= items.length;

  const handleClick = useCallback(() => {
    setIndex((index) => index + 1);
  }, []);

  const handleClickBack = useCallback(() => {
    setIndex((index) => index - 1);
  }, []);

  return (
    <>
      {!showConnexion && (
        <Block>
          <div style={{ padding: "1.4rem" }}>
            <img src={items[index].image} alt="" style={{ maxWidth: "100%" }} />

            <p
              style={{
                color: style.primary500,
                fontWeight: 700,
                fontSize: "1.75rem",
              }}
            >
              {items[index].name}
            </p>

            <p style={{ fontSize: "1.375rem", marginTop: "0.375rem" }}>
              {items[index].description}
            </p>

            <Button
              color="secondary"
              onClick={handleClick}
              style={{
                marginTop: "2.5rem",
                maxWidth: "100%",
                width: "330px",
                justifyContent: "center",
              }}
            >
              Continuer
            </Button>

            <div style={{ marginTop: "2.5rem" }}></div>

            <div style={{ postition: "absolute", bottom: "3rem" }}>
              <Mark $active={0 === index}></Mark>
              <Mark $active={1 === index}></Mark>
              <Mark $active={2 === index}></Mark>
            </div>
          </div>
        </Block>
      )}
      {showConnexion && (
        <BlockConnexion>
          <DescriptionContainer>
            <img src={logo} alt="" style={{ maxWidth: "400px" }} />
            <p style={{ fontSize: "1.375rem" }}>
              Agissez concrètement dans votre quartier et faites gagner Jean-Luc
              Mélenchon&nbsp;
              <InlineBlock>en 2022 !</InlineBlock>
            </p>
          </DescriptionContainer>

          <BackgroundTriangle>
            <div></div>
          </BackgroundTriangle>

          <ButtonContainer>
            <Button
              color="primary"
              onClick={handleClickBack}
              style={{
                marginTop: "2.5rem",
                maxWidth: "100%",
                width: "330px",
                justifyContent: "center",
              }}
            >
              Je crée mon compte
            </Button>
            <Button
              color="secondary"
              onClick={handleClickBack}
              style={{
                marginTop: "0.5rem",
                marginLeft: "0px",
                maxWidth: "100%",
                width: "330px",
                justifyContent: "center",
              }}
            >
              Je dispose déjà d'un compte
            </Button>
          </ButtonContainer>
        </BlockConnexion>
      )}
    </>
  );
};

export default IntroApp;
