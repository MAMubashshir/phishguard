// PhishGuard custom JavaScript

document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.classList.remove("show");
            alert.classList.add("fade");
        }, 5000);
    });

    // Confirm before submitting quiz if not all questions answered
    const quizForm = document.querySelector("form[action*='/quiz/']");
    if (quizForm) {
        quizForm.addEventListener("submit", function (e) {
            const radioGroups = {};
            quizForm.querySelectorAll("input[type=radio]").forEach(function (input) {
                radioGroups[input.name] = radioGroups[input.name] || false;
                if (input.checked) radioGroups[input.name] = true;
            });
            const allAnswered = Object.values(radioGroups).every(Boolean);
            if (!allAnswered) {
                e.preventDefault();
                alert("Please answer all questions before submitting.");
            }
        });
    }
});
