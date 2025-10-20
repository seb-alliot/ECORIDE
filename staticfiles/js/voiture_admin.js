function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {
    // URL complète vers la vue Django
    const ModelVoiture = "/ECORIDE/model-voiture/";

    const marqueSelect = document.querySelector("#id_marque");
    const modeleSelect = document.querySelector("#id_modele");

    if (!marqueSelect || !modeleSelect) return;

    marqueSelect.addEventListener("change", () => {
        const marque = marqueSelect.value;

        // Efface les anciens modèles
        modeleSelect.innerHTML = '<option value="">-- Sélectionnez un modèle --</option>';
        if (!marque) return;

        fetch(`${ModelVoiture}?marque=${marque}`, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
        .then(response => {
            // Vérifie si la réponse est JSON
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Réponse non JSON reçue !");
            }
            return response.json();
        })
        .then(data => {
            data.modeles.forEach(([value, label]) => {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = label;
                modeleSelect.appendChild(option);
            });
        })
        .catch(err => console.error("❌ Erreur de chargement des modèles :", err));
    });
});
