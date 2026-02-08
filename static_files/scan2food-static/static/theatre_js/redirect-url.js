const theatre_id = JSON.parse(document.getElementById('theatre-id').innerText);

function startCountdown() {
    // Create dark overlay
    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background = "rgba(0, 0, 0, 0.8)";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.zIndex = "9999";

    // Create modal container
    const modal = document.createElement("div");
    modal.style.width = "200px";
    modal.style.height = "200px";
    modal.style.borderRadius = "50%";
    modal.style.background = "linear-gradient(135deg, #4a90e2, #50e3c2)";
    modal.style.display = "flex";
    modal.style.flexDirection = "column";
    modal.style.alignItems = "center";
    modal.style.justifyContent = "center";
    modal.style.boxShadow = "0 8px 20px rgba(0, 0, 0, 0.4)";
    modal.style.position = "relative";
    modal.style.transition = "transform 0.3s ease";
    modal.style.animation = "pulse 1s infinite alternate";
    overlay.appendChild(modal);

    // Create countdown text
    const countdown = document.createElement("div");
    countdown.style.fontSize = "60px";
    countdown.style.fontWeight = "bold";
    countdown.style.color = "white";
    countdown.style.userSelect = "none";
    modal.appendChild(countdown);

    // Create cancel button
    const button = document.createElement("button");
    button.textContent = "Cancel";
    button.style.position = "absolute";
    button.style.bottom = "-60px";
    button.style.padding = "10px 25px";
    button.style.fontSize = "16px";
    button.style.border = "none";
    button.style.borderRadius = "8px";
    button.style.cursor = "pointer";
    button.style.backgroundColor = "#ff4d4d";
    button.style.color = "white";
    button.style.transition = "background-color 0.3s";
    button.onmouseover = () => (button.style.backgroundColor = "#ff1a1a");
    button.onmouseout = () => (button.style.backgroundColor = "#ff4d4d");
    modal.appendChild(button);

    document.body.appendChild(overlay);

    // Add keyframes for pulse animation
    const style = document.createElement("style");
    style.textContent = `
        @keyframes pulse {
          0% { transform: scale(1); }
          100% { transform: scale(1.1); }
        }
      `;
    document.head.appendChild(style);

    // Countdown logic
    let timeLeft = 10;
    countdown.textContent = timeLeft;

    const timer = setInterval(() => {
        timeLeft--;
        countdown.textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timer);
            overlay.remove();
            window.location.href = `/theatre/single-qr/${theatre_id}`; // Redirect URL
        }
    }, 1000);

    // Cancel redirect
    button.addEventListener("click", () => {
        clearInterval(timer);
        overlay.remove();
        // alert("Redirect canceled!");
    });
}

// Auto-start countdown
// startCountdown();
