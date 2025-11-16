document.addEventListener('DOMContentLoaded', function () {
    const voitureSelect = document.getElementById('id_voiture');
    const placesInput = document.getElementById('id_places');

    const select = document.createElement('select');
    select.setAttribute('name', placesInput.getAttribute('name'));

    placesInput.replaceWith(select);

    addDefaultOption(select);

    updateSeatsOption(voitureSelect, select);

    voitureSelect.addEventListener('change', function () {
        updateSeatsOption(voitureSelect, select);
    });
});

function addDefaultOption(select) {
    const option = document.createElement('option');
    option.value = '';
    option.textContent = '-- Sélectionnez un véhicule --';
    select.appendChild(option);
}

function updateSeatsOption(voitureSelect, select) {
    const voitureId = voitureSelect.value;
    const maxPlaces = voituresData[voitureId];

    clearSeatOptions(select);

    if (!maxPlaces) {
        return;
    }

    for (let i = 1; i <= maxPlaces; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `${i} place${i > 1 ? 's' : ''}`;
        select.appendChild(option);
    }
}

function clearSeatOptions(select) {
    while (select.options.length > 1) {
        select.remove(1);
    }
}
