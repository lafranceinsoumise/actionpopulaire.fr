import React, {useState} from "react";
import {useMobileApp, useNotificationGrant} from "../../../front/components/app/hooks";
import NotificationRationaleModal from "../../../events/components/agendaPage/NotificationRationaleModal";
import ActionCard from "../../../front/components/genericComponents/ActionCard";

export default function NotificationGrantedPanel() {
    const {isMobileApp} = useMobileApp();
    const {notificationIsGranted} = useNotificationGrant()
    const [openModal, setOpenModal] = useState(false);

    console.log('notification ?', notificationIsGranted);

    return <>
        {isMobileApp && !notificationIsGranted &&
            <>
                <NotificationRationaleModal shouldOpen={openModal}/>
                <ActionCard
                    text="Vos notifications sont désactivées. Activez-les pour ne rien rater."
                    iconName="bell"
                    confirmLabel="Activer"
                    onConfirm={() => setOpenModal(true)}
                >
                </ActionCard>

            </>
        }
    </>
}