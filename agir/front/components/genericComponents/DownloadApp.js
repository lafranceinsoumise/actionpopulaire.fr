import React from "react";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import logo from "@agir/front/genericComponents/logos/action-populaire_primary_mini.svg";

const StyledContainer = styled.div`
  display: flex;
  align-items: center;
  background-color: ${style.primary500};
  color: #fff;
  justify-content: space-evenly;
`;

const Title = styled.div``;
const Description = styled.div``;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  padding: 12px;

  ${Title} {
    color: ${style.secondary500};
    font-weight: 700;
    font-size: 15px;
  }

  ${Description} {
    color: #fff;
    font-size: 12px;
    flex-wrap: wrap;
  }
`;

const DownloadMinus = styled(Button)`
  border-radius: 50px;
  background-color: #fff;
  width: 52px;
  height: 52px;
  color: ${style.primary500};
  font-size: 13px;
  font-weight: 700;
  justify-content: center;

  @media (min-width: 380px) {
    display: none;
  }
`;

const Download = styled(Button)`
  background-color: #fff;
  color: ${style.primary500};
  font-size: 13px;
  font-weight: 700;
  justify-content: center;

  @media (max-width: 380px) {
    display: none;
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

export const DownloadApp = () => {
  return (
    <StyledContainer>
      <div style={{ padding: "0.5rem" }}>
        <FeatherIcon
          name="x"
          color="#fff"
          width="7px"
          height="7px"
          style={{ width: "7px", height: "7px" }}
        />
      </div>
      <img src={logo} alt="" style={{ width: "52px", height: "52px" }} />
      <Content>
        <Title>ACTION POPULAIRE</Title>
        <Description>
          Téléchargez l’appli des actions près{" "}
          <InlineBlock>de chez vous</InlineBlock>
        </Description>
      </Content>
      <div style={{ paddingRight: "18px" }}>
        <DownloadMinus as="a" href="#">
          <FeatherIcon name="download" color={style.primary500} />
        </DownloadMinus>
        <Download as="a" href="#">
          Télécharger
        </Download>
      </div>
    </StyledContainer>
  );
};

export default DownloadApp;
