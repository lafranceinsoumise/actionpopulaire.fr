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
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  text-align: center;

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
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-align: center;
  flex-direction: column;
  width: 100%;
  align-items: center;
  padding: 1rem;
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

const PurpleTriangle = styled.div`
  width: 100%;
  background-color: ${style.primary500};
  margin-top: -1px;
  div {
    background-color: white;
    height: 80px;
    margin-bottom: -1px;
    clip-path: polygon(0px 100%, 100% 0px, 100% 100%, 0px 100%);
  }
`;

const HeaderImage = styled.div`
  background-color: #fff;
  position: relative;
  padding-bottom: 90px;
  width: 100%;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;

  img {
    width: 90%;
    max-width: 358px;
    position: absolute;
    bottom: 0;
  }
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
    setIndex(0);
  }, []);

  return (
    <>
      {!showConnexion && (
        <Block>
          <HeaderImage>
            <PurpleTriangle style={{ paddingTop: "120px" }}>
              <div></div>
            </PurpleTriangle>

            <img src={items[index].image} />
          </HeaderImage>

          <div style={{ paddingTop: "47px" }}>
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

            <StyledButton color="secondary" onClick={handleClick}>
              Continuer
            </StyledButton>

            <div style={{ marginTop: "3rem", marginBottom: "1.5rem" }}>
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
            <div>
              <img src={logo} alt="" style={{ maxWidth: "300px" }} />
              <p
                style={{
                  fontSize: "1.375rem",
                  fontSize: "20px",
                  paddingTop: "2rem",
                }}
              >
                Agissez concrètement dans votre quartier et faites gagner
                Jean-Luc Mélenchon&nbsp;
                <InlineBlock>en 2022 !</InlineBlock>
              </p>
            </div>
          </DescriptionContainer>

          <BackgroundTriangle>
            <div></div>
          </BackgroundTriangle>

          <ButtonContainer>
            <StyledButton color="primary" onClick={handleClickBack}>
              Je crée mon compte
            </StyledButton>
            <StyledButton
              color="secondary"
              onClick={handleClickBack}
              style={{ marginTop: "0.5rem", marginLeft: "0px" }}
            >
              Je dispose déjà d'un compte
            </StyledButton>
          </ButtonContainer>
        </BlockConnexion>
      )}
    </>
  );
};

export default IntroApp;
