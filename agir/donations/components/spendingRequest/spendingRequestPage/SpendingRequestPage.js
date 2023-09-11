import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";
import useSWR from "swr";
import useSWRImmutable from "swr/immutable";

import * as api from "@agir/donations/spendingRequest/common/api";
import { useToast } from "@agir/front/globalContext/hooks";

import { Button } from "@agir/donations/common/StyledComponents";
import AttachmentModal from "@agir/donations/spendingRequest/common/AttachmentModal";
import BackLink from "@agir/front/app/Navigation/BackLink";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import { Hide } from "@agir/front/genericComponents/grid";
import DeleteAttachmmentModalConfirmation from "./DeleteAttachmentModalConfirmation";
import DeleteSpendingRequestButton from "./DeleteSpendingRequestButton";
import SpendingRequestDetails from "./SpendingRequestDetails";
import ValidateSpendingRequestButton from "./ValidateSpendingRequestButton";
import { useInView } from "@react-spring/core";

const StyledNav = styled(Hide).attrs((attrs) => ({
  ...attrs,
  as: "nav",
}))`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-left: auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    z-index: 10;
    isolation: isolate;
    position: sticky;
    bottom: -2px;
    left: 0;
    right: 0;
    width: 100%;
    flex-flow: column nowrap;
    align-items: stretch;
    background-color: white;
    gap: 0.5rem;
    margin: 0;
    padding: 2rem 1.5rem;
    box-shadow: ${(props) =>
      props.$stuck ? props.theme.elaborateShadow : "none"};
    border-top: ${(props) =>
      props.$stuck ? "1px solid " + props.theme.black100 : "none"};
    border-collapse: collapse;
  }
`;

const StyledPage = styled.main`
  padding: 2rem 0;
  max-width: 70rem;
  margin: 0 auto;
  min-height: 50vh;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1.5rem 0 0;
    max-width: 100%;
  }

  & > header {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding: 0 1.5rem;
      margin: 0;
    }

    & > * {
      flex: 0 0 auto;
    }

    h2 {
      font-size: 1.625rem;
      font-weight: 700;
      margin: 0;
      margin-right: auto;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        font-size: 1.375rem;
      }
    }
  }
`;

const SpendingRequestPage = ({ spendingRequestPk }) => {
  const { data: _session, isLoading: isSessionLoading } =
    useSWRImmutable("/api/session/");

  const {
    data: spendingRequest,
    isLoading: isSpendingRequestLoading,
    mutate,
  } = useSWR(
    api.getSpendingRequestEndpoint("getSpendingRequest", {
      spendingRequestPk,
    })
  );

  const isReady = !isSpendingRequestLoading && !isSessionLoading;
  const attachments = spendingRequest?.attachments;
  const status = spendingRequest?.status.code;

  const [selectedAttachment, setSelectedAttachment] = useState(null);
  const [attachmentAction, setAttachmentAction] = useState(null);
  const [isLoadingAttachment, setIsLoadingAttachment] = useState(false);
  const [attachmentError, setAttachmentError] = useState(null);

  const sendToast = useToast();
  const [navRef, navIsInView] = useInView({ threshold: 1 });
  console.log(navIsInView);

  const handleEditAttachment = useCallback(
    (id) => {
      const attachment =
        id && attachments && attachments.find((a) => a.id === id);
      setSelectedAttachment(attachment || {});
      setAttachmentAction("edit");
    },
    [attachments]
  );

  const handleDeleteAttachment = useCallback(
    (id) => {
      const attachment =
        id && attachments && attachments.find((a) => a.id === id);
      setSelectedAttachment(attachment || null);
      setAttachmentAction("delete");
    },
    [attachments]
  );

  const handleUnselectAttachment = useCallback(() => {
    setSelectedAttachment(null);
    setAttachmentAction(null);
  }, []);

  const saveAttachment = useCallback(
    async (attachment) => {
      setIsLoadingAttachment(true);
      setAttachmentError(null);
      const { _data, error } = attachment.id
        ? await api.updateDocument(attachment.id, attachment)
        : await api.createDocument(spendingRequestPk, attachment);

      if (error) {
        setIsLoadingAttachment(false);
        return setAttachmentError(error);
      }
      setSelectedAttachment(null);
      setIsLoadingAttachment(false);
      const updatedRequest = await mutate();
      sendToast(
        updatedRequest.status.code !== status
          ? "La pièce a été enregistrée et le statut de la demande mis à jour"
          : "La pièce justificative a été enregistrée",
        "SUCCESS"
      );
    },
    [mutate, sendToast, spendingRequestPk, status]
  );

  const deleteAttachment = useCallback(
    async (attachmentPk) => {
      setIsLoadingAttachment(true);
      setAttachmentError(null);
      const { error } = await api.deleteDocument(attachmentPk);

      if (error) {
        setIsLoadingAttachment(false);
        return setAttachmentError(error);
      }

      mutate((spendingRequest) => ({
        ...spendingRequest,
        attachments: spendingRequest.attachments.filter(
          (a) => a.id !== attachmentPk
        ),
      }));
      setSelectedAttachment(null);
      setIsLoadingAttachment(false);
    },
    [mutate]
  );

  return (
    <PageFadeIn ready={isReady} wait={<Skeleton />}>
      {isReady && spendingRequest && (
        <StyledPage>
          <BackLink style={{ marginLeft: 0 }} />
          <header>
            <h2>Demande de dépense</h2>
            <StyledNav $under>
              <DeleteSpendingRequestButton
                spendingRequest={spendingRequest}
                disabled={!spendingRequest.status.deletable}
              />
              <Button
                link
                route="editSpendingRequest"
                routeParams={{ spendingRequestPk }}
                title={
                  !spendingRequest.status.editable
                    ? "Cette demande ne peut pas être modifiée"
                    : "Modifier la demande"
                }
                disabled={!spendingRequest.status.editable}
                icon="edit-2"
              >
                Modifier
              </Button>
              <ValidateSpendingRequestButton
                spendingRequestPk={spendingRequest.id}
                action={spendingRequest.status.action}
                onValidate={mutate}
              />
            </StyledNav>
          </header>
          <Hide as={Spacer} size="1rem" $under />
          {spendingRequest && (
            <SpendingRequestDetails
              spendingRequest={spendingRequest}
              onAttachmentAdd={handleEditAttachment}
              onAttachmentChange={
                spendingRequest.status.editable
                  ? handleEditAttachment
                  : undefined
              }
              onAttachmentDelete={
                spendingRequest.status.editable
                  ? handleDeleteAttachment
                  : undefined
              }
            />
          )}
          <StyledNav ref={navRef} $over $stuck={!navIsInView}>
            <DeleteSpendingRequestButton
              spendingRequest={spendingRequest}
              disabled={!spendingRequest.status.deletable}
            />
            <Button
              link
              route="editSpendingRequest"
              routeParams={{ spendingRequestPk }}
              title={
                !spendingRequest.status.editable
                  ? "Cette demande ne peut pas être modifiée"
                  : "Modifier la demande"
              }
              disabled={!spendingRequest.status.editable}
              icon="edit-2"
            >
              Modifier
            </Button>
            <ValidateSpendingRequestButton
              spendingRequestPk={spendingRequest.id}
              action={spendingRequest.status.action}
              onValidate={mutate}
            />
          </StyledNav>
          <AttachmentModal
            value={selectedAttachment}
            shouldShow={attachmentAction === "edit" && !!selectedAttachment}
            onClose={handleUnselectAttachment}
            onChange={saveAttachment}
            isLoading={isLoadingAttachment}
            error={attachmentError}
            warning={spendingRequest.status.editionWarning}
          />
          <DeleteAttachmmentModalConfirmation
            attachment={
              attachmentAction === "delete" ? selectedAttachment : null
            }
            onClose={handleUnselectAttachment}
            onConfirm={deleteAttachment}
            isLoading={isLoadingAttachment}
            error={attachmentError}
          />
        </StyledPage>
      )}
    </PageFadeIn>
  );
};

SpendingRequestPage.propTypes = {
  spendingRequestPk: PropTypes.string,
};

export default SpendingRequestPage;
