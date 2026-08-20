function urlBase64ToUint8Array(value) {
    const padding = "=".repeat((4 - (value.length % 4)) % 4);
    const base64 = (value + padding).replace(/-/g, "+").replace(/_/g, "/");
    return Uint8Array.from(atob(base64), (character) => character.charCodeAt(0));
}

function getCsrfToken() {
    const token = document.cookie.split("; ").find((item) => item.startsWith("csrftoken="));
    return token ? decodeURIComponent(token.split("=")[1]) : "";
}

async function postJson(url, body = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
        body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "요청에 실패했습니다.");
    return data;
}

document.addEventListener("DOMContentLoaded", async () => {
    const enableButton = document.querySelector("#enable-push");
    const disableButton = document.querySelector("#disable-push");
    const status = document.querySelector("#push-status");
    if (!enableButton) return;

    if (!enableButton.dataset.publicKey) {
        enableButton.textContent = "알림 키 설정 필요";
        enableButton.disabled = true;
        if (status) status.textContent = "서버에 VAPID 공개키를 설정하면 브라우저 알림을 사용할 수 있습니다.";
        return;
    }

    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
        enableButton.textContent = "알림을 지원하지 않는 브라우저입니다";
        enableButton.disabled = true;
        if (status) status.textContent = "현재 브라우저에서는 푸시 알림을 사용할 수 없습니다.";
        return;
    }

    const registration = await navigator.serviceWorker.register("/sw.js");

    async function refreshState() {
        const subscription = await registration.pushManager.getSubscription();
        enableButton.textContent = subscription ? "테스트 알림 보내기" : "알림 켜기";
        if (disableButton) disableButton.hidden = !subscription;
        if (status) {
            status.textContent = subscription
                ? "이 브라우저에서 푸시 알림을 받고 있습니다."
                : "현재 브라우저의 푸시 알림이 꺼져 있습니다.";
        }
        return subscription;
    }

    enableButton.addEventListener("click", async () => {
        enableButton.disabled = true;
        try {
            let subscription = await registration.pushManager.getSubscription();
            if (subscription) {
                await postJson(enableButton.dataset.testUrl);
                enableButton.textContent = "알림 전송 완료";
                setTimeout(refreshState, 1500);
            } else {
                const permission = await Notification.requestPermission();
                if (permission !== "granted") throw new Error("알림 권한을 허용해 주세요.");
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(enableButton.dataset.publicKey),
                });
                await postJson(enableButton.dataset.subscribeUrl, subscription.toJSON());
                await refreshState();
            }
        } catch (error) {
            alert(error.message);
        } finally {
            enableButton.disabled = false;
        }
    });

    if (disableButton) {
        disableButton.addEventListener("click", async () => {
            disableButton.disabled = true;
            try {
                const subscription = await registration.pushManager.getSubscription();
                if (subscription) {
                    await postJson(enableButton.dataset.unsubscribeUrl, { endpoint: subscription.endpoint });
                    await subscription.unsubscribe();
                }
                await refreshState();
            } catch (error) {
                alert(error.message);
            } finally {
                disableButton.disabled = false;
            }
        });
    }

    await refreshState();
});
