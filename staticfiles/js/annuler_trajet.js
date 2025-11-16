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
    const trajets5 = JSON.parse(document.getElementById('trajet5').textContent);

    // Récupère l'URL depuis le data attribute
    const btn = document.getElementById('annuler-btn');
    const annulerUrl = btn.dataset.url;

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
            window.location.reload();
        }
    })
    .catch(err => console.error("Erreur fetch:", err));
}

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById('annuler-btn');
    if (btn) {
        btn.addEventListener("click", annulerTrajets5);
    }
});
