document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("email_select");

    select.addEventListener("change", function () {
        document.getElementById("email_select_form").submit();
    });
});