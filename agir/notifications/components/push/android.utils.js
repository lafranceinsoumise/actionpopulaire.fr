import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

export function notificationPermissionIsGranted() {
    return androidApp?.notificationPermissionIsGranted() ?? false;
}

export function askNotificationPermission() {
    androidApp?.setupNotificationPermission();
}