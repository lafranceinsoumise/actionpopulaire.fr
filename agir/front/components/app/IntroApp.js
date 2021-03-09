import { useState } from 'react';
import React from 'react';
import Button from "@agir/front/genericComponents/Button";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import img1 from "../genericComponents/images/introApp1.jpg";

const Mark = styled.span`
  width: 24px;
  height: 4px;
  margin: 3px;
  display: inline-block;
  background-color: ${(props) => (
    props.$active ? style.primary500 : style.black200
  )};
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

const IntroApp = () => {

  const [index, setIndex] = useState(0);

  const items = [{
    name: "Rencontrez",
    description: "d'autres membres et agissez ensemble !",
    image: img1
  },
  {
    name: "Agissez concrètement",
    description: "formez-vous et commandez du matériel, tracts et affiches !",
    image: img1
  },
  {
    name: "Organisez et rejoignez",
    description: "une équipe de soutien autour de vous !",
    image: img1
  }];

  const handleClick = () => {
    if (index >= items.length - 1)
    {
      console.log("Redirect into app !");
      return;
    }
    setIndex(index + 1);
  };

  return (
    <Block>
      <img src={items[index].image} alt="" style={{maxWidth: "100%"}} />

      <p style={{color: style.primary500, fontWeight: 700, fontSize: "1.75rem"}}>
        {items[index].name}
      </p>

      <p style={{fontSize: "1.375rem", marginTop: "0.375rem"}}>
        {items[index].description}
      </p>

      <Button color="secondary" onClick={() => handleClick()} 
        style={{marginTop: "2.5rem", maxWidth:"100%", width: "330px", justifyContent:"center"}}>
        Continuer
      </Button>

      <div style={{marginTop: "2.5rem"}}></div>

      <div style={{postition: "absolute", bottom: "3rem"}}>
        <Mark $active={(0 === index)}></Mark>
        <Mark $active={(1 === index)}></Mark>
        <Mark $active={(2 === index)}></Mark>
      </div>
    </Block>
  );
};
  
export default IntroApp;
