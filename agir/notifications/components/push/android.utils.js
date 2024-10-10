

export function androidNotificationPermissionIsGranted() {
    return window.androidApp?.notificationPermissionIsGranted() ?? false;
}

export function askNotificationPermission() {
    window.androidApp?.setupNotificationPermission();
}