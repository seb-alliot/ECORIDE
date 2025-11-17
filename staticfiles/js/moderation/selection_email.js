document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("email_type");

    select.addEventListener("change", function () {
        document.getElementById("email_filter_form").submit();
    });
});