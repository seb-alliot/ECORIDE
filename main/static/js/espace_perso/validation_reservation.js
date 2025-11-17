document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reservation_form');

    if (form) {
        form.addEventListener('submit', function(event) {

            const confirmation = confirm('Confirmer la réservation?');

            if (!confirmation) {
                event.preventDefault();
            }
        });
    }
});