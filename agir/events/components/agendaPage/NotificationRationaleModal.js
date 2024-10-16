import React, {useCallback, useEffect, useState} from "react";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import {useMobileApp} from "@agir/front/app/hooks";
import styled from "styled-components";
import {useLocalStorage} from "../../../lib/components/utils/hooks";
import {useNotificationGrant} from "../../../front/components/app/hooks";
import {usePush} from "@agir/notifications/push/subscriptions";

const BellTitle = styled.div`
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
`

export default function NotificationRationaleModal({ shouldOpen, onClose }) {
    const {isAndroid, isIOS} = useMobileApp();
    const [userDeclinedNotification, setUserDeclinedNotification] = useLocalStorage("AP__userDeclinedNotification", false);
    const {notificationIsGranted, grantNotification} = useNotificationGrant()
    const [modalOpen, setModalOpen] = useState(!notificationIsGranted && (isAndroid || isIOS) && !userDeclinedNotification);
    const { subscribe } = usePush()

    useEffect(() => {
        if (shouldOpen) {
            setModalOpen(true)
        }
    }, [shouldOpen]);

    useEffect(() => {
        if (notificationIsGranted && modalOpen) {
            setUserDeclinedNotification(false);
            setModalOpen(false);
            subscribe();
            onClose?.()
        }
    }, [notificationIsGranted])

    const onConfirm = useCallback(() => {
        grantNotification?.();
    }, [grantNotification]);

    const onDismiss = useCallback(() => {
        setUserDeclinedNotification(true);
        setModalOpen(false);
        onClose?.()
    }, []);

    return <ModalConfirmation confirmationLabel="Ok pour moi"
                              dismissLabel="Une prochaine fois"
                              onDismiss={onDismiss}
                              onConfirm={onConfirm}
                              onClose={() => setModalOpen(false)}
                              shouldShow={modalOpen}>
        <BellTitle><span className="fa-regular fa-bell fa-2xl"/></BellTitle>
        <p>Nous allons vous demander un accès aux notifications.
            Elles vous permettent par exemple de connaître des événements proches de chez vous, de vous tenir au courant des nouvelles de vos groupes.
            <br />
            Les notifications
            peuvent être désactivées ou activées via votre profil.</p>
    </ModalConfirmation>
}