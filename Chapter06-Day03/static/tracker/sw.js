self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("push", (event) => {
    const data = event.data ? event.data.json() : {};
    event.waitUntil(
        self.registration.showNotification(data.title || "우선콕", {
            body: data.body || "새 알림이 있습니다.",
            data: { url: data.url || "/" },
            tag: data.tag || "priority-poke",
            renotify: true,
        })
    );
});

self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    event.waitUntil(clients.openWindow(event.notification.data.url || "/"));
});
