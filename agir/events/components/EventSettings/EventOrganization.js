import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";
import * as api from "@agir/events/common/api";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import SearchAndSelectField from "@agir/front/formComponents/SearchAndSelectField";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import MemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

const EventOrganization = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );

  const [value, setValue] = useState("");
  const [options, setOptions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const group = {
    email: "pole@group.com",
    displayName: "Pôle groupe d'action",
  };
  const members = [
    { email: "pascal@preprod.com", displayName: "Pascal Preprod" },
    { email: "pascal@preprod.com", displayName: "Pascal Preprod" },
  ];

  const handleChange = (value) => {
    setValue(value);
  };

  const handleSearch = async (q) => {
    await new Promise((resolve) => {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        if (!q) {
          setOptions(defaultOptions);
        } else {
          setOptions(
            defaultOptions.filter((option) => {
              return option.label.toLowerCase().includes(q.toLowerCase);
            })
          );
        }
        resolve();
      }, 3000);
    });
  };

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Co-organisation</StyledTitle>

      <Spacer size="1rem" />

      <span style={{ color: style.black700 }}>
        Invitez des groupes à organiser votre événement.Ils s’afficheront sur la
        page publiquement.
      </span>

      <Spacer size="1rem" />

      <SearchAndSelectField
        value={value}
        onChange={handleChange}
        onSearch={handleSearch}
        isLoading={isLoading}
        defaultOptions={options}
      />

      <MemberList members={[group]} />

      <Spacer size="1rem" />
    </>
  );
};
EventOrganization.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventOrganization;
