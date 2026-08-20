self.addEventListener("push", (event) => {
    const data = event.data ? event.data.json() : {};
    event.waitUntil(
        self.registration.showNotification(data.title || "과제신호등", {
            body: data.body || "새 알림이 있습니다.",
            data: { url: data.url || "/" },
            tag: data.tag || "assignment-signal",
        })
    );
});

self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    event.waitUntil(clients.openWindow(event.notification.data.url || "/"));
});
