document.addEventListener("DOMContentLoaded", function() {
    console.log("=== SCRIPT CHARGÉ ===");

    const filtreForm = document.getElementById("filtre_form");
    const resultatsContainer = document.getElementById("resultats");
    const reservationBtn = document.getElementById("reservation_btn");

    console.log("filtreForm:", filtreForm);
    console.log("resultatsContainer:", resultatsContainer);
    console.log("reservationBtn:", reservationBtn);

    if (filtreForm && resultatsContainer && reservationBtn) {
        console.log("✅ Tous les éléments trouvés !");

        filtreForm.addEventListener("submit", function(event) {
            event.preventDefault();
            console.log("=== FORMULAIRE SOUMIS ===");

            const note = filtreForm.querySelector('[name="note"]').value;
            const temps_trajet = filtreForm.querySelector('[name="temps_trajet"]').value;
            const prix = filtreForm.querySelector('[name="prix"]').value;
            const urlParams = new URLSearchParams(window.location.search);
            const ville_depart = urlParams.get('ville_depart') || '';
            const ville_arrivee = urlParams.get('ville_arrivee') || '';
            const date = urlParams.get('date') || '';
            const pseudo = urlParams.get('pseudo') || '';


            console.log("Note:", note);
            console.log("Temps:", temps_trajet);
            console.log("Prix:", prix);

            const params = new URLSearchParams({note, temps_trajet, prix, ville_depart, ville_arrivee, date, pseudo});
            const url = `${urlfiltre_form}?${params.toString()}`;

            console.log("URL:", url);

            resultatsContainer.innerHTML = '<p class="class_flex class_justify_center">Chargement en cours...</p>';

            fetch(url, {
                method: "GET",
                headers: {"X-Requested-With": "XMLHttpRequest"}
            })
            .then(response => {
                console.log("Response status:", response.status);
                if (!response.ok) throw new Error("Erreur réseau ou du serveur.");
                return response.json();
            })
            .then(data => {
                console.log("Data reçue:", data);
                if (data.html) {
                    resultatsContainer.innerHTML = data.html;
                    const hasResultats = resultatsContainer.querySelectorAll('ul.resultat li').length > 0;
                    console.log("Résultats trouvés:", hasResultats);
                    reservationBtn.style.display = hasResultats ? "flex" : "none";
                } else {
                    resultatsContainer.innerHTML = "<p class='class_flex class_justify_center'>Aucun résultat trouvé.</p>";
                    reservationBtn.style.display = "none";
                }
            })
            .catch(error => {
                console.error("❌ Erreur:", error);
                resultatsContainer.innerHTML = "<p class='class_flex class_justify_center'>Une erreur s'est produite.</p>";
                reservationBtn.style.display = "none";
            });
        });
    } else {
        console.error("❌ Éléments manquants :");
        if (!filtreForm) console.error("  - filtre_form introuvable");
        if (!resultatsContainer) console.error("  - resultats introuvable");
        if (!reservationBtn) console.error("  - reservation_btn introuvable");
    }
});