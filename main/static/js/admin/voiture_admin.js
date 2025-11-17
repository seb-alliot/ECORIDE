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
    const ModelVoiture = "/ECORIDE/model-voiture/";
    const marqueSelect = document.querySelector("#id_marque");
    const modeleSelect = document.querySelector("#id_modele");

    if (!marqueSelect || !modeleSelect) return;


    const marqueDefaultValue = "-- Sélectionnez une marque --";

    if (marqueSelect.options.length === 0 || marqueSelect.options[0].value !== "") {
        const defaultWaitingOption = document.createElement("option");
        defaultWaitingOption.value = "";
        defaultWaitingOption.textContent = marqueDefaultValue;
        marqueSelect.prepend(defaultWaitingOption);

        marqueSelect.value = "";
    }

    if (modeleSelect.options.length === 0 || modeleSelect.options[0].value !== "") {
        const defaultWaitingOption = document.createElement("option");
        defaultWaitingOption.value = "";
        defaultWaitingOption.textContent = "-- Sélectionnez une marque --";
        modeleSelect.prepend(defaultWaitingOption);
        modeleSelect.value = "";
        modeleSelect.disabled = true;
    }

    marqueSelect.addEventListener("change", () => {
        const marque = marqueSelect.value;
        modeleSelect.disabled = true;

        modeleSelect.innerHTML = '<option value="">-- Chargement des modèles... --</option>';

        if (!marque) {
            modeleSelect.innerHTML = '<option value="">-- Sélectionnez une marque --</option>';
            return;
        }

        fetch(`${ModelVoiture}?marque=${marque}`, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
        .then(response => {
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Réponse non JSON reçue !");
            }
            return response.json();
        })
        .then(data => {
            modeleSelect.innerHTML = '';

            if (data.modeles.length > 0) {
                const defaultModelOption = document.createElement("option");
                defaultModelOption.value = "";
                defaultModelOption.textContent = "-- Sélectionnez un modèle --";
                modeleSelect.appendChild(defaultModelOption);
            } else {
                const noModelOption = document.createElement("option");
                noModelOption.value = "";
                noModelOption.textContent = "-- Aucun modèle trouvé --";
                modeleSelect.appendChild(noModelOption);
            }

            data.modeles.forEach(([value, label]) => {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = label;
                modeleSelect.appendChild(option);
            });

            if (data.modeles.length > 0) {
                modeleSelect.remove(0);

                modeleSelect.selectedIndex = 0;
            }

            modeleSelect.disabled = false;
        })
        .catch(err => {
            console.error("❌ Erreur de chargement des modèles :", err);
            modeleSelect.innerHTML = '<option value="">-- Erreur de chargement --</option>';
            modeleSelect.disabled = true;
        });
    });
});