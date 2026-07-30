(function () {
    "use strict";

    const canvas = document.getElementById("wheelCanvas");
    if (!canvas) return; // Locked dashboard view has no wheel — nothing to do.

    const ctx = canvas.getContext("2d");
    const size = canvas.width;
    const center = size / 2;
    const radius = center - 10;

    const segments = window.API_POOL;
    const segmentAngle = (2 * Math.PI) / segments.length;

    const colors = [
        "#6c5ce7", "#00cec9", "#fd79a8", "#fdcb6e",
        "#0984e3", "#e17055", "#00b894", "#a29bfe",
        "#e84393", "#74b9ff", "#55efc4", "#ffeaa7",
        "#d63031", "#81ecec", "#fab1a0", "#636e72",
        "#aca3e9", "#956e6e"
    ];

    let currentRotation = 0; // radians, tracks cumulative wheel rotation
    let spinning = false;

    function drawWheel(rotation) {
        ctx.clearRect(0, 0, size, size);
        ctx.save();
        ctx.translate(center, center);
        ctx.rotate(rotation);

        segments.forEach((label, i) => {
            const start = i * segmentAngle;
            const end = start + segmentAngle;

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.arc(0, 0, radius, start, end);
            ctx.closePath();
            ctx.fillStyle = colors[i % colors.length];
            ctx.fill();
            ctx.strokeStyle = "#10142a";
            ctx.lineWidth = 2;
            ctx.stroke();

            // Draw label
            ctx.save();
            ctx.rotate(start + segmentAngle / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "#0f1220";
            ctx.font = "bold 13px 'Segoe UI', sans-serif";
            ctx.fillText(label, radius - 14, 5);
            ctx.restore();
        });

        ctx.restore();
    }

    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        return match ? decodeURIComponent(match[2]) : null;
    }

    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    /**
     * Animate the wheel from its current rotation to a target rotation
     * so that `targetIndex` segment center ends up under the top pointer.
     */
    function animateToIndex(targetIndex, onDone) {
        const segmentCenter = targetIndex * segmentAngle + segmentAngle / 2;
        // Pointer is at the top (angle = -90deg = -PI/2 in canvas coords,
        // but since we draw starting at angle 0 = 3 o'clock, we need the
        // segment center to align with -PI/2 after rotation).
        const targetPointerAngle = -Math.PI / 2;

        // Normalize current rotation within [0, 2PI)
        const normalizedCurrent = currentRotation % (2 * Math.PI);

        // We want: normalizedCurrent + segmentCenter + delta ≡ targetPointerAngle (mod 2PI)
        // Add several full extra spins for visual effect.
        const extraSpins = 5 + Math.floor(Math.random() * 3); // 5-7 full spins
        let desiredFinal = targetPointerAngle - segmentCenter;
        // Bring desiredFinal into a range greater than currentRotation
        while (desiredFinal < currentRotation) {
            desiredFinal += 2 * Math.PI;
        }
        desiredFinal += extraSpins * 2 * Math.PI;

        const startRotation = currentRotation;
        const totalDelta = desiredFinal - startRotation;
        const duration = 3800; // ms
        const startTime = performance.now();

        function step(now) {
            const elapsed = now - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = easeOutCubic(t);
            currentRotation = startRotation + totalDelta * eased;
            drawWheel(currentRotation);

            if (t < 1) {
                requestAnimationFrame(step);
            } else {
                currentRotation = desiredFinal % (2 * Math.PI);
                if (typeof onDone === "function") onDone();
            }
        }
        requestAnimationFrame(step);
    }

    drawWheel(currentRotation);

    const spinBtn = document.getElementById("spinBtn");
    const errorBox = document.getElementById("spinError");
    const spinCountDisplay = document.getElementById("spin-count-display");
    const assignedSoFar = document.getElementById("assignedSoFar");

    function showError(message) {
        if (!errorBox) return;
        errorBox.textContent = message;
        errorBox.style.display = "block";
    }

    function hideError() {
        if (!errorBox) return;
        errorBox.style.display = "none";
    }

    function addAssignedCard(label, apiName) {
        if (!assignedSoFar) return;
        const card = document.createElement("div");
        card.className = "api-card small";
        card.innerHTML =
            '<span class="api-card-label">' + label + '</span>' +
            '<span class="api-card-name">' + apiName + '</span>';
        assignedSoFar.appendChild(card);
    }

    async function handleSpin() {
        if (spinning) return;
        hideError();
        spinning = true;
        spinBtn.disabled = true;

        try {
            const response = await fetch(window.SPIN_URL, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
            });
            const data = await response.json();

            if (!data.success) {
                showError(data.error || "Something went wrong. Please try again.");
                spinning = false;
                spinBtn.disabled = false;
                return;
            }

            animateToIndex(data.wheel_index, function () {
                spinning = false;
                const label = data.spin_count === 1 ? "API #1" : "API #2";
                addAssignedCard(label, data.chosen_api);

                if (spinCountDisplay) spinCountDisplay.textContent = data.spin_count;

                if (data.is_locked) {
                    spinBtn.disabled = true;
                    spinBtn.textContent = "LOCKED";
                    // Reload after a short pause to show the full locked dashboard.
                    setTimeout(function () {
                        window.location.reload();
                    }, 1600);
                } else {
                    spinBtn.disabled = false;
                }
            });
        } catch (err) {
            showError("Network error. Please try again.");
            spinning = false;
            spinBtn.disabled = false;
        }
    }

    if (spinBtn) {
        spinBtn.addEventListener("click", handleSpin);
    }
})();
