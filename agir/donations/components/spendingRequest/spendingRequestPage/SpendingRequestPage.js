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
import { useIsDesktop } from "@agir/front/genericComponents/grid";
import DeleteAttachmmentModalConfirmation from "./DeleteAttachmentModalConfirmation";
import DeleteSpendingRequestButton from "./DeleteSpendingRequestButton";
import SpendingRequestDetails from "./SpendingRequestDetails";
import ValidateSpendingRequestButton from "./ValidateSpendingRequestButton";

const StyledPage = styled.main`
  padding: 2rem;
  max-width: 70rem;
  margin: 0 auto;
  min-height: 50vh;

  nav {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin: 0 0 1.25rem;
      flex-flow: column-reverse nowrap;
      justify-content: space-between;
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

    div {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-left: auto;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        gap: 0.5rem;
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

  const isDesktop = useIsDesktop();
  const isReady = !isSpendingRequestLoading && !isSessionLoading;
  const attachments = spendingRequest?.attachments;
  const status = spendingRequest?.status;

  const [selectedAttachment, setSelectedAttachment] = useState(null);
  const [attachmentAction, setAttachmentAction] = useState(null);
  const [isLoadingAttachment, setIsLoadingAttachment] = useState(false);
  const [attachmentError, setAttachmentError] = useState(null);

  const sendToast = useToast();

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
        updatedRequest.status !== status
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
          <nav>
            <h2>Demande de dépense</h2>
            <div>
              <DeleteSpendingRequestButton
                spendingRequest={spendingRequest}
                disabled={!spendingRequest.deletable}
              />
              <Button
                link
                route="editSpendingRequest"
                routeParams={{ spendingRequestPk }}
                title={
                  !spendingRequest.editable
                    ? "Cette demande ne peut pas être modifiée"
                    : "Modifier la demande"
                }
                disabled={!spendingRequest.editable}
                small={!isDesktop}
                icon="edit-2"
              >
                Modifier
              </Button>
              <ValidateSpendingRequestButton
                spendingRequest={spendingRequest}
                onValidate={mutate}
              />
            </div>
          </nav>
          <Spacer size="1rem" />
          {spendingRequest && (
            <SpendingRequestDetails
              spendingRequest={spendingRequest}
              onAttachmentAdd={handleEditAttachment}
              onAttachmentChange={
                spendingRequest?.editable ? handleEditAttachment : undefined
              }
              onAttachmentDelete={
                spendingRequest?.editable ? handleDeleteAttachment : undefined
              }
            />
          )}
          <AttachmentModal
            value={selectedAttachment}
            shouldShow={attachmentAction === "edit" && !!selectedAttachment}
            onClose={handleUnselectAttachment}
            onChange={saveAttachment}
            isLoading={isLoadingAttachment}
            error={attachmentError}
            warning={spendingRequest?.editionWarning}
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
