document.addEventListener('DOMContentLoaded', function () {
    const voitureSelect = document.getElementById('id_voiture');

    /** @type HTMLElement|null */
    const placesInput = document.getElementById('id_places');

    const name = placesInput.getAttribute('name')
    const select = document.createElement('select');

    select.setAttribute('name', name)

    placesInput.replaceWith(select);
    const defaultOption = document.createElement('option');
    defaultOption.value = ''
    defaultOption.textContent = '-- Sélectionnez un véhicule --'


    select.appendChild(defaultOption);

    updateSeatsOption(voitureSelect, select);

    voitureSelect.addEventListener('change', function () {
        updateSeatsOption(voitureSelect, select);
    });
});

/**
 * @param { HTMLSelectElement } select
 */
function updateSeatsOption(voitureSelect, select) {
    const voitureId = voitureSelect.value;
    const maxPlaces = voituresData[voitureId];

    if (maxPlaces) {
        removeOptions(select)

        for (let i = 0; i < maxPlaces; i++) {
            /** @type { HTMLOptionElement } */
            const option = document.createElement('option')

            option.value = i + 1;
            option.textContent = i + 1 + " place";

            if(i >= 1) {
                option.textContent += "s";
            }

            select.add(option)
        }
    }
}

function removeOptions(selectElement) {
    var i, L = selectElement.options.length - 1;

    for(i = L; i >= 0; i--) {
        selectElement.remove(i);
    }
}