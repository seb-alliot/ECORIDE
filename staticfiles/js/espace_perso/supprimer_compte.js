document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('suppression_compte_form');

    const suppressionButton = document.getElementById('suppression-compte');

    if (form && suppressionButton) {
        form.addEventListener('submit', function(event) {

            const confirmation = confirm('Confirmer la suppression du compte ?');

            if (!confirmation) {
                event.preventDefault();
            }
        });
    }
});