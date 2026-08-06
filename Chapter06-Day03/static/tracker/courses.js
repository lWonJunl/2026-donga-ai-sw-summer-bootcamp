document.addEventListener("DOMContentLoaded", () => {
    const collection = document.querySelector("[data-course-collection]");
    const buttons = document.querySelectorAll(".view-button[data-view]");
    if (!collection || !buttons.length) return;

    function setView(view) {
        const nextView = view === "list" ? "list" : "card";
        collection.dataset.view = nextView;
        buttons.forEach((button) => {
            const selected = button.dataset.view === nextView;
            button.classList.toggle("active", selected);
            button.setAttribute("aria-pressed", String(selected));
        });
        localStorage.setItem("priority-poke-group-view", nextView);
    }

    buttons.forEach((button) => {
        button.addEventListener("click", () => setView(button.dataset.view));
    });
    setView(localStorage.getItem("priority-poke-group-view") || "card");
});
