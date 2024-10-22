import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import React, {useEffect, useMemo, useState} from "react";
import {useLocalStorage} from "@agir/lib/utils/hooks";
import styled from "styled-components";
import useSWR from "swr";
import {getNewsletterStatus} from "@agir/notifications/common/notifications.config";
import {updateProfile} from "@agir/front/authentication/api";

const StyledTitle = styled.div`
    color: ${(props) => props.theme.primary500};
    text-align: center;
    
    span {
        margin-bottom: 25px;
    }
`
const StyledModalContent = styled.div`
    text-align: center;
    padding: 10px;
`


export default function ModalMissingNewsletter() {
    const [alreadyShowNewsletterModal, setAlreadyShowNewsletterModal] = useLocalStorage("AP_show_newsletter_modal", false)
    const {data: profile, mutate: mutateProfile, isLoading} = useSWR("/api/user/profile/");
    const newsletterOptions = useMemo(() => getNewsletterStatus(profile?.newsletters), [profile]);

    function userRegisteredToReguliere() {
        return newsletterOptions?.["LFI_reguliere"]?.email ?? false
    }

    async function inscription() {
        const updatedProfile = await updateProfile({"newsletters": ["LFI_reguliere"]});
        await mutateProfile(() => updatedProfile?.data)
        setAlreadyShowNewsletterModal(true)
    }

    function userOldEnough() {
        const dateLessOneMonth = new Date()
        dateLessOneMonth.setMonth(dateLessOneMonth.getMonth() - 1)
        return new Date(profile?.created) < dateLessOneMonth;
    }

    useEffect(() => {
        if (userRegisteredToReguliere() && !alreadyShowNewsletterModal) {
            setAlreadyShowNewsletterModal(true)
        }
    }, [newsletterOptions, alreadyShowNewsletterModal]);

    const show = !alreadyShowNewsletterModal && !isLoading && !userRegisteredToReguliere() && userOldEnough()

    return <ModalConfirmation
        shouldShow={show}
        title={<StyledTitle>
            <span className="fa-regular fa-envelope fa-2xl"/><br/>
            NE MANQUEZ PAS NOS ACTUALITÉS !
            </StyledTitle>}
        dismissLabel="Non merci"
        confirmationLabel="Je m'inscris"
        onConfirm={inscription}
        onClose={() => setAlreadyShowNewsletterModal(true)}
        shouldDismissOnClick={false}
    >
        <StyledModalContent>

            <p>Cela fait un moment que vous utilisez Action populaire, mais vous n'êtes toujours pas inscrit⸱e à la
                lettre d'information de la France Insoumise.</p>
            <p>Inscrivez-vous dès maintenant pour suivre de près par e-mail toutes les actualités du mouvement !</p>
        </StyledModalContent>
    </ModalConfirmation>
}