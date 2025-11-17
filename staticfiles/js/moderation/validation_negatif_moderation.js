document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('moderation_form');

    if (form) {
        form.addEventListener('submit', function(event) {

            const confirmation = confirm('Confirmer votre choix ?');

            if (!confirmation) {
                event.preventDefault();
            }
        });
    }
});