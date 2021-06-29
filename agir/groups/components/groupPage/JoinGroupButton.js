import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useLocation } from "react-router-dom";
import { mutate } from "swr";

import * as api from "@agir/groups/groupPage/api";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

import Button from "@agir/front/genericComponents/Button";

const JoinGroupButton = (props) => {
  const { id } = props;
  const location = useLocation();

  const user = useSelector(getUser);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = useCallback(
    async (e) => {
      e && e.preventDefault();
      setIsLoading(true);
      let redirectTo = "";
      try {
        const response = await api.joinGroup(id);
        if (response.error) {
          redirectTo = response.error.redirectTo;
        }
      } catch (err) {
        // Reload current page if an unhandled error occurs
        window.location.reload();
      }
      if (redirectTo) {
        window.location = redirectTo;
        return;
      }
      setIsLoading(false);
      mutate(
        api.getGroupPageEndpoint("getGroup", { groupPk: id }),
        (group) => ({ ...group, isMember: true })
      );
    },
    [id]
  );

  if (!user) {
    return (
      <div>
        <Button
          as="Link"
          color="success"
          route="login"
          params={{
            from: "group",
            next: location.pathname,
          }}
        >
          Rejoindre le groupe
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <Button type="submit" color="success" disabled={isLoading}>
        Rejoindre le groupe
      </Button>
    </form>
  );
};

JoinGroupButton.propTypes = {
  id: PropTypes.string.isRequired,
};
export default JoinGroupButton;
