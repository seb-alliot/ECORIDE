document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("email_select");
    const form = document.getElementById("email_select_form");

    if (!select || !form) {
        console.log("Élément select ou form introuvable, script ignoré");
        return;
    }

    select.addEventListener("change", function () {
        form.submit();
    });

    if (select.value === "" || select.value === null) {
        console.log("Aucune sélection faite, formulaire non soumis");
    }
});
