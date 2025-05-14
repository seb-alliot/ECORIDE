document.addEventListener('DOMContentLoaded', function () {
    // Sélectionne tous les formulaires sur la page
    const forms = document.querySelectorAll('form');
    const tabs = document.querySelectorAll('input[name="tab-group-1"]'); // Tous les boutons radio des onglets

    // Fonction pour sauvegarder l'onglet actif
    function saveActiveTab() {
        const activeTab = document.querySelector('input[name="tab-group-1"]:checked');
        if (activeTab) {
            localStorage.setItem('activeTab', activeTab.id); // Sauvegarder l'ID de l'onglet actif
        }
    }

    // Ajouter un écouteur pour chaque formulaire
    forms.forEach(form => {
        form.addEventListener('submit', function () {
            saveActiveTab(); // Sauvegarder l'onglet actif avant la soumission du formulaire
        });
    });

    // Restaurer l'onglet actif après le rechargement de la page
    const savedTabId = localStorage.getItem('activeTab');
    if (savedTabId) {
        const savedTab = document.getElementById(savedTabId);
        if (savedTab) savedTab.checked = true;
    }

});
