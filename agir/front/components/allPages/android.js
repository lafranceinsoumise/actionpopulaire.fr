import React, {useCallback, useEffect, useState} from "react";
import {getDefaultNotifications} from "@agir/notifications/common/notifications.config";
import {createSubscriptions} from "@agir/notifications/common/api";
import {useMobileApp} from "@agir/front/app/hooks";

export function androidNotificationPermissionIsGranted() {
    return window.androidApp?.notificationPermissionIsGranted() ?? false;
}

export function askNotificationPermission() {
    window.androidApp?.setupNotificationPermission();
}

let grantObservers = [];
export function useAndroidNotificationGrant() {
    const [androidNotificationGranted, setAndroidNotificationGranted] = useState(androidNotificationPermissionIsGranted())
    const {isMobileApp, isAndroid} = useMobileApp();


    const grantNotification = useCallback(() => {
        if (isAndroid) {
            askNotificationPermission();
        } else if (isIOS) {
            //TODO do the same for iOS
        }
    }, [isMobileApp])

    const onAndroidMessage = useCallback((message) => {
        if (message.channel === "NOTIFICATION" && message.value === "granted") {
            grantObservers.forEach((obs) => obs(true));
            async function setupDefaultNotification() {
                /**
                 * we must send subscribe for each notification type because if
                 * we send as a list, and there is only on which is already registered, the API will trigger a constraint and ignore the other ones.
                 */
                const subscriptionRequest = getDefaultNotifications().map((notification) => {
                    return notification.activityTypes.map((type) =>
                        createSubscriptions([{
                            activityType: type,
                            type: "push",
                        }]));
                });
                await Promise.all(subscriptionRequest.flat(2))
            }
            setupDefaultNotification();
        }
    }, []);


    useEffect(() => {
        if (!window.onAndroidMessage) {
            window.onAndroidMessage = (message) => {
                onAndroidMessage(message);
            }
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