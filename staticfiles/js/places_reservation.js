

document.addEventListener('DOMContentLoaded', function () {
    const placesInput = document.getElementById('id_places');
    const wrapper = document.getElementById('place_a_reserver');

    const maxPlaces = parseInt(wrapper.dataset.maxPlaces, 10);

    if (!placesInput || isNaN(maxPlaces)) return;

    const name = placesInput.getAttribute('name');
    const select = document.createElement('select');
    select.setAttribute('name', name);
    select.id = 'id_places';

    placesInput.replaceWith(select);

    for (let i = 1; i <= maxPlaces; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i + ' place' + (i > 1 ? 's' : '');
        select.appendChild(option);
    }
});
