import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { mutate } from "swr";

import * as api from "@agir/groups/groupPage/api";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

import Button from "@agir/front/genericComponents/Button";
import SubscriptionTypeModal from "@agir/front/authentication/SubscriptionTypeModal";

const JoinGroupButton = (props) => {
  const { id, is2022 = false } = props;
  const history = useHistory();
  const location = useLocation();

  const user = useSelector(getUser);
  const [isLoading, setIsLoading] = useState(false);

  const [hasSubscriptionTypeModal, setHasSubscriptionTypeModal] =
    useState(false);

  const openSubscriptionTypeModal = useCallback((e) => {
    e && e.preventDefault();
    setHasSubscriptionTypeModal(true);
  }, []);

  const closeSubscriptionTypeModal = useCallback(() => {
    setHasSubscriptionTypeModal(false);
  }, []);

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
      setHasSubscriptionTypeModal(false);
      mutate(
        api.getGroupPageEndpoint("getGroup", { groupPk: id }),
        (group) => ({ ...group, isMember: true })
      );
    },
    [id]
  );

  const shouldUpdateSubscription = useMemo(() => {
    if (!user) {
      return null;
    }
    if (is2022 && user.is2022) {
      return null;
    }
    if (!is2022 && user.isInsoumise) {
      return null;
    }
    return is2022 ? "NSP" : "LFI";
  }, [user, is2022]);

  if (!user) {
    return (
      <div>
        <Button
          as="Link"
          color="success"
          route="login"
          params={{
            from: "group",
            forUsers: is2022 ? "2" : "I",
            next: location.pathname,
          }}
        >
          Rejoindre {is2022 ? "l'équipe" : "le groupe"}
        </Button>
      </div>
    );
  }

  return (
    <form
      onSubmit={
        shouldUpdateSubscription ? openSubscriptionTypeModal : handleSubmit
      }
    >
      <Button type="submit" color="success" disabled={isLoading}>
        Rejoindre {is2022 ? "l'équipe" : "le groupe"}
      </Button>
      {shouldUpdateSubscription ? (
        <SubscriptionTypeModal
          shouldShow={hasSubscriptionTypeModal}
          type={shouldUpdateSubscription}
          target="group"
          onConfirm={handleSubmit}
          onCancel={closeSubscriptionTypeModal}
          isLoading={isLoading}
        />
      ) : null}
    </form>
  );
};

JoinGroupButton.propTypes = {
  id: PropTypes.string.isRequired,
  is2022: PropTypes.bool,
};
export default JoinGroupButton;
