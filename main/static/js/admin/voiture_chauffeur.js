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
    const ModelVoiture = "/ECORIDE/voiture-chauffeur/";
    const chauffeurSelect = document.querySelector("#id_chauffeur");
    const modeleSelect = document.querySelector("#id_voiture");
    const placesSelect = document.querySelector("#id_places");

    if(chauffeurSelect) {
        chauffeurSelect.addEventListener("change", () => {
            const selectedChauffeur = chauffeurSelect.value;

            // Correction: parenthèses au lieu de backticks
            fetch(`${ModelVoiture}?id_chauffeur=${selectedChauffeur}`, {
                method: "GET",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
            })
            .then(response => response.json())
            .then(data => {
                // Remplir le select des voitures
                modeleSelect.innerHTML = '<option value="">---------</option>';

                if (data.voitures && data.voitures.length > 0) {
                    data.voitures.forEach(voiture => {
                        const option = document.createElement("option");
                        option.value = voiture.id; // L'ID pour le formulaire
                        option.textContent = `${voiture.marque} ${voiture.modele}`; // Affichage pour l'utilisateur
                        modeleSelect.appendChild(option);
                    });
                }

                // Remplir le select des places (de 1 au max)
                placesSelect.innerHTML = '<option value="">---------</option>';

                if (data.max_places && data.max_places > 0) {
                    for (let i = 1; i <= data.max_places; i++) {
                        const option = document.createElement("option");
                        option.value = i;
                        option.textContent = `${i} place${i > 1 ? 's' : ''}`;
                        placesSelect.appendChild(option);
                    }
                }
            })
            .catch(error => {
                console.error("Erreur lors de la récupération des modèles de voiture :", error);
            });
        });
    }
});