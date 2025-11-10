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
    const trajets5 = JSON.parse(document.getElementById('label_proposition').textContent);

    fetch(annulerUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            trajet: trajets5.map(t => t.id)
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.nb_annules > 0) {
            // reload uniquement si des trajets ont été annulés
            window.location.reload();
        }
    })
    .catch(err => console.error("Erreur fetch:", err));
}

// Attendre que le DOM soit prêt
document.addEventListener("DOMContentLoaded", annulerTrajets5);
