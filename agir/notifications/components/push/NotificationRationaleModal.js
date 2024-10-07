import Modal from "@agir/front/genericComponents/Modal";
import {useEffect} from "react";


export default function NotificationRationaleModal() {

    useEffect(() => {

    }, []);

    return <Modal>
        <p>Nous allons vous demander un accès aux notifications,
            nous envoyons des notifications pour vous alerter des évènements proches de chez vous. Les notifications peuvent être désactivées ou activées via le panel des notifications.</p>
    </Modal>
}