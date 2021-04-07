import React, { useState, useEffect } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";


const Assets = styled.div`
  margin-left: 3rem;
  display: inline-flex;
`;

const Asset = styled.div`
  border: 1px solid #ddd;
  padding: 4px 10px;
  margin-right: 4px;
  display: inline-block;
  font-size: 12px;
`;

const Member = styled.div`
  
border: 1px solid yellow;
font-size: 1rem;

> div:first-child {
  display: flex;
  flex-direction: row;
  align-items: center;
  }

  img {
    width: 2rem;
    height: 2rem;
    margin-right: 1rem;
  }
`;

const Role = styled.span`
  color: ${style.primary500};
  margin-left: 0.5rem;
`;

const Email = styled.span`
  color: ${style.black500};
  margin-left: 0.5rem;
`;

const ShowMore = styled.span`
  color: ${style.primary500};
  cursor: pointer;

  :hover {
    text-decoration: underline;
  }
`;

const DEFAULT_MEMBER = {
  img: <RawFeatherIcon
    name="user"
    width="1.5rem"
    height="1.5rem"
    style={{padding: "0.25rem", backgroundColor: style.primary500, color: "#fff", borderRadius: "40px", marginRight: "1rem"}}
  />,
  name: "Jean-Luc Mélenchon",
  role: "Administrateur",
  email: "example@mail.fr",
  //assets: ["Député", "Journaliste", "Blogueur"]
  assets: ["Député", "Journaliste", "Blogueur", "Artiste", "Informaticien"]
};

const GroupMember = () => {

  const [assets, setAssets] = useState(DEFAULT_MEMBER.assets.length ? DEFAULT_MEMBER.assets.slice(0, 3) : []);
  //const [showMore, setShowMore] = useState(DEFAULT_MEMBER.assets?.length > 3);
  const [showMore, setShowMore] = useState(true);

  const handleShowMore = () => {
    setAssets(DEFAULT_MEMBER.assets);
    setShowMore(false);
  };

  return (<>
    <Member>
      <div>
        {DEFAULT_MEMBER.img}
        <span>{ DEFAULT_MEMBER.name }</span>
        <Role>({DEFAULT_MEMBER.role})</Role>
        <Email>{DEFAULT_MEMBER.email}</Email>
      </div>
      <Assets>
        {assets.map((e, id) => ( 
          <Asset key={id}>{e}</Asset>
          ))}
      </Assets>
      {showMore && <ShowMore onClick={handleShowMore}>Voir +</ShowMore> }
    </Member>
  </>);
};

export default GroupMember;

