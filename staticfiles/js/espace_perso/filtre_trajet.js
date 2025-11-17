document.addEventListener("DOMContentLoaded", function() {
    const filtreForm = document.getElementById("filtre_form");
    const resultatsContainer = document.getElementById("resultats");
    const reservationBtn = document.getElementById("reservation_btn");

    if (filtreForm && resultatsContainer && reservationBtn) {
        filtreForm.addEventListener("submit", function(event) {
            event.preventDefault();

            // Récupération des valeurs directement en JS
            const note = filtreForm.querySelector('[name="note"]').value;
            const temps_trajet = filtreForm.querySelector('[name="temps_trajet"]').value;
            const prix = filtreForm.querySelector('[name="prix"]').value;

            const params = new URLSearchParams({note, temps_trajet, prix});
            const url = `${urlfiltre_form}?${params.toString()}`;

            resultatsContainer.innerHTML = '<p class="class_flex class_justify_center">Chargement en cours...</p>';

            fetch(url, {
                method: "GET",
                headers: {"X-Requested-With": "XMLHttpRequest"}
            })
            .then(response => {
                if (!response.ok) throw new Error("Erreur réseau ou du serveur.");
                return response.json();
            })
            .then(data => {
                if (data.html) {
                    resultatsContainer.innerHTML = "";
                    resultatsContainer.innerHTML = data.html;

                    const hasResultats = resultatsContainer.querySelectorAll('ul.resultat li').length > 0;
                    reservationBtn.style.display = hasResultats ? "flex" : "none";
                } else {
                    resultatsContainer.innerHTML = "<p class='class_flex class_justify_center'>Aucun résultat trouvé.</p>";
                    reservationBtn.style.display = "none";
                }
            })
            .catch(error => {
                console.error("Erreur:", error);
                resultatsContainer.innerHTML = "<p class='class_flex class_justify_center'>Une erreur s'est produite.</p>";
                reservationBtn.style.display = "none";
            });
        });
    }
});
