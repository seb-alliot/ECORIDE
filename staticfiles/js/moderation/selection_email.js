document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("email_type");
    const form = document.getElementById("email_filter_form");

    if (!select || !form) return; 

    select.addEventListener("change", function () {
        form.submit();
    });
    if (select.value === "" || select.value === null) {
        console.log("Aucun changement sélectionné, formulaire non soumis");
    }
});
