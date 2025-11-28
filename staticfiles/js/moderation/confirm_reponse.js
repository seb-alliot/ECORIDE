document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("contact_form");
    const boutton = document.getElementById("bout_reponse_modo");

    boutton.addEventListener("click", (event) => {
        const ok = confirm("Êtes-vous sûr de votre réponse ?");
        if (!ok) {
            event.preventDefault(); // Empêche l’envoi du formulaire
        }
    });
});
