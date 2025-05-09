document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    document.querySelectorAll(".plan-card button").forEach(button => {
        button.addEventListener("click", () => {
            alert("🚲 Subscription feature coming soon!");
        });
    });

    document.querySelectorAll(".plan-card").forEach(card => {
        card.addEventListener("mouseenter", () => {
            card.style.boxShadow = "0 6px 15px rgba(0,0,0,0.2)";
        });
        card.addEventListener("mouseleave", () => {
            card.style.boxShadow = "0 4px 8px rgba(0,0,0,0.1)";
        });
    });
});
