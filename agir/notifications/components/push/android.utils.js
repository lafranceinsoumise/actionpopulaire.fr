


export function askNotificationPermission() {
    // global var setup by the Android webview to trigger the notification permission
    if (androidApp) {
        androidApp.setupNotificationPermission();
    }

}