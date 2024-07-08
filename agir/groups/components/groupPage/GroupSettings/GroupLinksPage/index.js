import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";
import { mutate } from "swr";

import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";

import GroupLinks from "./GroupLinks";
import GroupLinkForm from "./GroupLinkForm";

import { useGroup } from "@agir/groups/groupPage/hooks/group";
import {
  getGroupEndpoint,
  saveGroupLink,
  deleteGroupLink,
} from "@agir/groups/utils/api";
import { useToast } from "@agir/front/globalContext/hooks";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const FormPanelWrapper = styled(animated.div)`
  position: absolute;
  top: 0;
  left: 0;
  padding: 2rem;
  background-color: ${(props) => props.theme.background0};
  width: 100%;
  height: 100%;
  box-shadow: ${(props) => props.theme.elaborateShadow};
`;

const GroupLinksPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const sendToast = useToast();

  const group = useGroup(groupPk);

  const [selectedLink, setSelectedLink] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const saveLink = useCallback(
    async (link) => {
      setErrors({});
      setIsLoading(true);
      const res = await saveGroupLink(groupPk, link);
      setIsLoading(false);

      if (res.error) {
        setErrors(res.error);
        return;
      }

      sendToast("Le lien a été enregistré", "SUCCESS", { autoClose: true });
      setSelectedLink(null);
      mutate(getGroupEndpoint("getGroup", { groupPk }));
    },
    [sendToast, groupPk],
  );

  const deleteLink = useCallback(
    async (linkPk) => {
      setIsLoading(true);
      const res = await deleteGroupLink(groupPk, linkPk);
      setIsLoading(false);

      if (res.error) {
        sendToast(
          "Le lien n'a pas pu être supprimé. Veuillez ressayer.",
          "ERROR",
          { autoClose: true },
        );
        return;
      }

      sendToast("Le lien a été supprimé", "SUCCESS", { autoClose: true });
      setSelectedLink(null);
      mutate(getGroupEndpoint("getGroup", { groupPk }));
    },
    [sendToast, groupPk],
  );

  const handleBack = useCallback(() => {
    setSelectedLink(null);
    setErrors({});
  }, []);

  const transition = useTransition(selectedLink, slideInTransition);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Liens et réseaux sociaux du groupe</StyledTitle>
      <Spacer size="1rem" />
      <PageFadeIn ready={!!group} wait={<Skeleton />}>
        <GroupLinks links={group.links} onEdit={setSelectedLink} />
      </PageFadeIn>
      {transition(
        (style, item) =>
          item && (
            <FormPanelWrapper style={style}>
              <GroupLinkForm
                onBack={handleBack}
                onSubmit={saveLink}
                onDelete={deleteLink}
                selectedLink={selectedLink}
                errors={errors}
                isLoading={isLoading}
              />
            </FormPanelWrapper>
          ),
      )}
    </>
  );
};
GroupLinksPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupLinksPage;
