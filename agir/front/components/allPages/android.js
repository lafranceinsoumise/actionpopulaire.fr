import React, {useCallback, useEffect, useState} from "react";
import {useMobileApp} from "@agir/front/app/hooks";
import {setupDefaultNotification} from "@agir/notifications/common/api";

export function androidNotificationPermissionIsGranted() {
    return window.androidApp?.notificationPermissionIsGranted() ?? false;
}

export function askNotificationPermission() {
    window.androidApp?.setupNotificationPermission();
}

let grantObservers = [];
export function useAndroidNotificationGrant(onNotificationGrant) {
    const [androidNotificationGranted, setAndroidNotificationGranted] = useState(androidNotificationPermissionIsGranted())
    const {isMobileApp} = useMobileApp();

    const grantNotification = useCallback(() => {
        askNotificationPermission();
    }, [isMobileApp])

    const onAndroidMessage = useCallback((message) => {
        if (message.channel === "NOTIFICATION" && message.value === "granted") {
            onNotificationGrant?.()
            grantObservers.forEach((obs) => obs(true));
        }
    }, []);


    useEffect(() => {
        if (!window.onAndroidMessage) {
            window.onAndroidMessage = onAndroidMessage
        }
        grantObservers.push(setAndroidNotificationGranted)
        return () => {
            const observerIndex = grantObservers.findIndex((obs) => obs === setAndroidNotificationGranted)
            grantObservers.splice(observerIndex, 1);
            if (grantObservers.length === 0) {
                window.onAndroidMessage = undefined
            }
        }
    }, []);


    return {
        notificationIsGranted: isMobileApp && androidNotificationGranted,
        grantNotification
    }

}