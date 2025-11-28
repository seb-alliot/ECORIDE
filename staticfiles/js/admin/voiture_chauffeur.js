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
            fetch(`${ModelVoiture}?id_chauffeur=${selectedChauffeur}`, {
                method: "GET",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
            })
            .then(response => response.json())
            .then(data => {
                modeleSelect.innerHTML = "";
                data.id_voiture.forEach(voiture => {
                    const option = document.createElement("option");
                    option.value = voiture;
                    option.textContent = voiture;
                    modeleSelect.appendChild(option);
                });
                placesSelect.innerHTML = "";
                data.id_places.forEach(place => {
                    const option = document.createElement("option");
                    option.value = place;
                    option.textContent = place;
                    placesSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Erreur lors de la récupération des modèles de voiture :", error);
            });
        });
    }
});
