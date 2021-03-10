import React, { useState, useCallback } from "react";
import Button from "@agir/front/genericComponents/Button";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import img1 from "../genericComponents/images/introApp1.jpg";
import logo from "../genericComponents/images/logoActionPopulaire.png";

const Mark = styled.span`
  width: 24px;
  height: 4px;
  margin: 3px;
  display: inline-block;
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

const InlineBlock = styled.span`
  display: inline-block;
`;

const items = [
  {
    name: "Rencontrez",
    description: "d'autres membres et agissez ensemble !",
    image: img1,
  },
  {
    name: "Agissez concrètement",
    description: "formez-vous et commandez du matériel, tracts et affiches !",
    image: img1,
  },
  {
    name: "Organisez et rejoignez",
    description: "une équipe de soutien autour de vous !",
    image: img1,
  },
];

const IntroApp = () => {
  const [index, setIndex] = useState(0);

  const handleClick = useCallback(() => {
    setIndex((index) => index + 1);
  }, []);

  const handleClickBack = useCallback(() => {
    setIndex((index) => index - 1);
  }, []);

  const showConnexion = index >= items.length;

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
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justify: "center",
            alignItems: "center",
          }}
        >
          <div
            style={{
              backgroundColor: style.secondary500,
              padding: "1.4rem",
              // height: "618px",
              display: "flex",
              justifyContent: "center",
              flexDirection: "column",
              alignItems: "center",
              position: "relative",
              width: "100%",
              textAlign: "center",
            }}
          >
            <img src={logo} alt="" style={{ maxWidth: "400px" }} />
            <p style={{ fontSize: "1.375rem" }}>
              Agissez concrètement dans votre quartier et faites gagner Jean-Luc
              Mélenchon
              <InlineBlock>en 2022 !</InlineBlock>
            </p>
          </div>

          <div style={{width: "100%", backgroundColor: style.secondary500}}>
            <div style={{backgroundColor: "white", height: "100px", 
              clipPath: "polygon(0px 100%, 100% 0px, 100% 100%, 0px 100%)"}}></div>
          </div>

          <div
            style={{
              marginBottom: "40px",
              display: "flex",
              flexAlign: "center",
              flexDirection: "column",
            }}
          >
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
          </div>
        </div>
      )}
    </>
  );
};

export default IntroApp;
