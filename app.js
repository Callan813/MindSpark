// ===== Login Function =====
function login() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    if (username === "admin" && password === "password") {
        // Store login state
        localStorage.setItem("isLoggedIn", "true");
        window.location.href = "welcome.html";
    } else {
        document.getElementById("error-message").textContent = "Invalid credentials. Try again.";
    }
}

// ===== Logout Function =====
function logout() {
    localStorage.removeItem("isLoggedIn");
    window.location.href = "login.html";
}

// ===== Check Login State =====
document.addEventListener("DOMContentLoaded", function() {
    // Check if we're on the welcome page
    if (window.location.pathname.includes("welcome.html")) {
        const isLoggedIn = localStorage.getItem("isLoggedIn");
        if (!isLoggedIn) {
            window.location.href = "login.html";
        }
    }

    // Initialize symbols animation
    const symbols = document.querySelectorAll(".productivity-symbol");
    symbols.forEach((symbol, index) => {
        // Add slight delay to each symbol's animation
        symbol.style.animationDelay = `${index * 0.2}s`;
    });
});

// ===== Symbol Placement & Animation =====
document.addEventListener("DOMContentLoaded", function () {
    const symbolsContainer = document.getElementById("symbols-container");
    const symbols = ["fa-lightbulb", "fa-clock", "fa-brain", "fa-chart-line", "fa-cogs"];
    
    // Define safe zones for symbol placement with more spacing
    const safeZones = [
        { top: "20%", left: "5%", right: "60%" },     // Top left zone
        { top: "20%", left: "70%", right: "5%" },     // Top right zone
        { top: "45%", left: "5%", right: "60%" },     // Middle zone
        { top: "70%", left: "5%", right: "60%" },     // Bottom left zone
        { top: "70%", left: "70%", right: "5%" }      // Bottom right zone
    ];
    
    symbols.forEach((symbolClass, index) => {
        let symbol = document.createElement("i");
        symbol.classList.add("fas", symbolClass, "productivity-symbol");
        // Add floating animation with same duration for all symbols
        symbol.style.animation = `float 3s ease-in-out infinite`;
        
        symbolsContainer.appendChild(symbol);
    });
});

// Add floating animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes float {
        0% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-20px);
        }
        100% {
            transform: translateY(0px);
        }
    }
    
    .productivity-symbol {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);
