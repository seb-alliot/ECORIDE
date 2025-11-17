document.addEventListener('DOMContentLoaded', function() {
    // 1. Ciblez les deux boutons par leurs IDs
    const ajouterButton = document.getElementById('ajouter');
    const refuserButton = document.getElementById('refuser');

    // Fonction générique pour gérer le clic
    function handleButtonClick(event) {
        const button = event.currentTarget;

        const actionValue = button.value;

        let confirmationMessage;
        if (actionValue === 'Ajouter') {
            confirmationMessage = 'Confirmer l\'ajout ?';
        } else if (actionValue === 'Refuser') {
            confirmationMessage = 'Confirmer le refus ?';
        } else {
            confirmationMessage = 'Confirmer l\'action ?';
        }

        const confirmation = confirm(confirmationMessage);

        if (!confirmation) {
            event.preventDefault();
        }
    }

    if (ajouterButton) {
        ajouterButton.addEventListener('click', handleButtonClick);
    }

    if (refuserButton) {
        refuserButton.addEventListener('click', handleButtonClick);
    }
});