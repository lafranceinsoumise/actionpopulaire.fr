import React, {useEffect, useState} from "react";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import {askNotificationPermission, androidNotificationPermissionIsGranted} from "@agir/notifications/push/android.utils";
import {useMobileApp} from "@agir/front/app/hooks";
import {createSubscriptions} from "../../../notifications/components/common/api";
import {getDefaultNotifications} from "../../../notifications/components/common/notifications.config";
import styled from "styled-components";
import {useLocalStorage} from "../../../lib/components/utils/hooks";
import {useError} from "react-use";
import {useNotificationGrant} from "../../../front/components/app/hooks";

const BellTitle = styled.div`
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
`

export default function NotificationRationaleModal({ shouldOpen }) {

    const {isAndroid, isIOS} = useMobileApp();
    const [userDeclinedNotification, setUserDeclinedNotification] = useLocalStorage("AP__userDeclinedNotification", false);
    const {notificationIsGranted, grantNotification} = useNotificationGrant()
    const [modalOpen, setModalOpen] = useState(!notificationIsGranted && (isAndroid || isIOS) && !userDeclinedNotification);

    useEffect(() => {
        if (shouldOpen) {
            setModalOpen(true)
        }
    }, [shouldOpen]);

    useEffect(() => {
        setUserDeclinedNotification(false);
    }, [notificationIsGranted])

    function onConfirm() {
        grantNotification();
        setModalOpen(false);
    }

    function onDismiss() {
        setUserDeclinedNotification(true);
        setModalOpen(false);
    }

    return <ModalConfirmation confirmationLabel="Ok pour moi"
                              dismissLabel="Une prochaine fois"
                              onDismiss={onDismiss}
                              onConfirm={onConfirm}
                              shouldShow={modalOpen}>
        <BellTitle><span className="fa-regular fa-bell fa-2xl"/></BellTitle>
        <p>Nous allons vous demander un accès aux notifications.
            Elles vous permettent par exemple de connaître des événements proches de chez vous, de vous tenir au courant des nouvelles de vos groupes.
            <br />
            Les notifications
            peuvent être désactivées ou activées via votre profil.</p>
    </ModalConfirmation>
}