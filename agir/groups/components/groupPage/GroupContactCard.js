import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { getGenderedWord } from "@agir/lib/utils/display";

import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

import Card from "./GroupPageCard";

const StyledReferentSection = styled.section`
  margin-bottom: 1.5rem;

  &:empty {
    display: none;
    margin: 0;
  }

  ${Avatar} {
    width: ${({ $length }) => ($length > 3 ? "3rem" : "4rem")};
    height: ${({ $length }) => ($length > 3 ? "3rem" : "4rem")};
  }

  ${Avatar} + ${Avatar} {
    margin-left: 4px;
  }

  && p {
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;

    &:nth-child(2) {
      font-size: 1.125rem;

      @media (max-width: ${style.collapse}px) {
        font-size: 1rem;
      }
    }

    && strong {
      font-weight: 600;
    }
  }
`;
const StyledContactSection = styled.p`
  font-size: 14px;
  line-height: 1.5;
  display: flex;
  flex-flow: column nowrap;
  margin: 0;

  && strong {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }

  && a {
    font-weight: 500;
    text-decoration: none;
    color: ${style.primary500};
    cursor: pointer;
  }
`;

const GroupContactCard = (props) => {
  const { referents, contact, editLinkTo } = props;

  const referentTitle = useMemo(() => {
    if (!Array.isArray(referents) || referents.length === 0) {
      return "";
    }
    const gender = referents.reduce((genders, referent) => {
      const gender = referent.gender || "?";
      return gender === genders ? genders : genders + gender;
    }, "");
    return `${getGenderedWord(
      gender,
      "Animateur·ice",
      "Animatrice",
      "Animateur"
    )}${referents.length > 1 ? "s" : ""}`;
  }, [referents]);

  if (!referents && !contact) {
    return null;
  }

  return (
    <Card>
      {Array.isArray(referents) && referents.length > 0 ? (
        <StyledReferentSection>
          <p>{referentTitle} du groupe</p>
        </StyledReferentSection>
      ) : null}
      {contact ? (
        <StyledContactSection>
          {contact.name && (
            <strong>
              Contact&ensp;
              {editLinkTo && (
                <Link to={editLinkTo}>
                  <RawFeatherIcon
                    name="edit-2"
                    color={style.black1000}
                    width="1rem"
                    height="1rem"
                  />
                </Link>
              )}
            </strong>
          )}
          {contact.name && <span>{contact.name}</span>}
          {contact.email && (
            <a href={`mailto:${contact.email}`}>{contact.email}</a>
          )}
          {contact.phone && (
            <span>
              {contact.phone} {contact.hidePhone && " (caché)"}
            </span>
          )}
        </StyledContactSection>
      ) : null}
    </Card>
  );
};

GroupContactCard.propTypes = {
  referents: PropTypes.arrayOf(
    PropTypes.shape({
      image: PropTypes.string,
      gender: PropTypes.string,
    })
  ),
  contact: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
  }),
  editLinkTo: PropTypes.string,
};
export default GroupContactCard;
