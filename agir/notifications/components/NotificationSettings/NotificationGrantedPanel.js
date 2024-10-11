import React, {useEffect, useState} from "react";
import {useMobileApp, useNotificationGrant} from "../../../front/components/app/hooks";
import NotificationRationaleModal from "../../../events/components/agendaPage/NotificationRationaleModal";
import ActionCard from "../../../front/components/genericComponents/ActionCard";
import {useError} from "react-use";

export default function NotificationGrantedPanel() {
    const {isMobileApp} = useMobileApp();
    const {notificationIsGranted} = useNotificationGrant()
    const [openModal, setOpenModal] = useState(false);

    return <>
        {isMobileApp && <NotificationRationaleModal
            onClose={() => setOpenModal(false)}
            shouldOpen={openModal}/>
        }
        {isMobileApp && !notificationIsGranted &&
            <>
                <ActionCard
                    text="Vos notifications mobiles sont désactivées. Activez-les pour ne rien rater."
                    iconName="bell"
                    confirmLabel="Activer"
                    onConfirm={() => setOpenModal(true)}
                >
                </ActionCard>

            </>
        }
    </>
}