document.addEventListener("DOMContentLoaded", () => {
    const delay = 100; // Delay in milliseconds
    setTimeout(() => {
        let navbar = document.querySelector(".navbar-home");
        if (navbar) {
            navbar.href = "/app/aura-hr"; // Update the URL
            console.log("Navbar URL successfully updated!");
        } else {
            console.error("Navbar element not found. Check the class name or DOM structure.");
        }
    }, delay);
});

