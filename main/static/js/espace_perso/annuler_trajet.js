
/**
 * Récupère la valeur d'un cookie par son nom
 * @param {string} name - Nom du cookie
 * @returns {string|null} - Valeur du cookie ou null
 */
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

function annulerTrajets5() {

    // Vérification de l'élément DOM contenant les trajets
    const trajetElement = document.getElementById('trajet5');
    if (!trajetElement) {
        return;
    }

    // Parsing JSON avec gestion d'erreur
    let trajets5;
    try {
        trajets5 = JSON.parse(trajetElement.textContent);
    } catch (error) {
        return;
    }

    // Validation du format des données
    if (!Array.isArray(trajets5)) {
        return;
    }

    // Vérification si des trajets existent
    if (trajets5.length === 0) {
        return;
    }

    // Requête AJAX avec gestion d'erreurs complète
    fetch(window.annulerUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            trajet: trajets5.map(t => t.id)
        })
    })
    .then(res => {
        // Vérification du statut HTTP
        if (!res.ok) {
            throw new Error(`Erreur HTTP ${res.status}: ${res.statusText}`);
        }
        return res.json();
    })
    .then(data => {
        if (data.success) {
            if (data.nb_annules > 0) {
                window.location.reload();
            } else {
                return;
            }
        } else {
            return;
        }
    })
    .catch(err => {

        // Feedback utilisateur en cas d'erreur
        if (err.message.includes('HTTP')) {
            alert('Erreur serveur. Impossible de nettoyer les trajets automatiquement. Veuillez réessayer.');
        } else {
            alert('Impossible de contacter le serveur. Vérifiez votre connexion internet.');
        }
    });
}

// Exécution au chargement de la page
document.addEventListener("DOMContentLoaded", () => {

    // Vérification que l'URL d'annulation est définie
    if (typeof window.annulerUrl === 'undefined') {
        return;
    }
    annulerTrajets5();
});