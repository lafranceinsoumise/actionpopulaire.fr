import React, { useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const Assets = styled.div`
  margin-left: 3rem;
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
`;

const Asset = styled.div`
  border: 1px solid #ddd;
  padding: 4px 10px;
  margin-right: 4px;
  margin-bottom: 4px;
  display: inline-block;
  font-size: 12px;
`;

const Name = styled.span``;

const Role = styled.span`
  color: ${style.primary500};
`;

const Email = styled.span`
  color: ${style.black500};
`;

const MemberInfos = styled.div`
  display: inline-flex;
  flex-wrap: wrap;

  ${Name}, ${Role} {
    margin-right: 0.5rem;
  }
`;

const Member = styled.div`
  font-size: 1rem;

  > div:first-child {
    display: flex;
    flex-direction: row;
    align-items: center;
  }
`;

const ShowMore = styled.span`
  color: ${style.primary500};
  cursor: pointer;
  margin-bottom: 4px;
  margin-left: 4px;

  :hover {
    text-decoration: underline;
  }
`;

const GroupMember = (props) => {
  const { name, role, email, assets } = props;

  const [customAssets, setCustomAssets] = useState(
    assets?.length ? assets.slice(0, 3) : []
  );
  const [showMore, setShowMore] = useState(assets?.length > 3);

  const handleShowMore = () => {
    setCustomAssets(assets);
    setShowMore(false);
  };

  return (
    <>
      <Member>
        <div>
          <RawFeatherIcon
            name="user"
            width="1.5rem"
            height="1.5rem"
            style={{
              padding: "0.25rem",
              backgroundColor: style.primary500,
              color: "#fff",
              borderRadius: "40px",
              marginRight: "1rem",
            }}
          />
          <MemberInfos>
            <Name>{name}</Name>
            <Role>({role})</Role>
            <Email>{email}</Email>
          </MemberInfos>
        </div>
        <Assets>
          {customAssets.map((e, id) => (
            <Asset key={id}>{e}</Asset>
          ))}
          {showMore && <ShowMore onClick={handleShowMore}>Voir +</ShowMore>}
        </Assets>
      </Member>
    </>
  );
};
GroupMember.propTypes = {
  name: PropTypes.string,
  role: PropTypes.string,
  email: PropTypes.string,
  assets: PropTypes.arrayOf(PropTypes.string),
};

export default GroupMember;
