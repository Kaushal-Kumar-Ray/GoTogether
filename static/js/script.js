let currentRideId = null;
let rideInterval = null;
let chatInterval = null;

/* ===================================================
   DOM READY INITIALIZER
=================================================== */
document.addEventListener("DOMContentLoaded", () => {
    initRideSystem();
    initChatSystem();
    initLeaveModal();
    initRequestModals();
});

/* ===================================================
   RIDE SYSTEM
=================================================== */

function initRideSystem() {
    const rideContainer = document.getElementById("rides-container");
    if (!rideContainer) return;

    fetchRides();
    rideInterval = setInterval(fetchRides, 3000);
}

async function fetchRides() {
    const container = document.getElementById("rides-container");
    if (!container) return;

    try {
        const response = await fetch("/rides/data" + window.location.search);
        const rides = await response.json();

        container.innerHTML = "";

        let ridesToShow = rides;

        if (!window.location.search) {
            ridesToShow = rides.filter(ride =>
                ride.is_creator || ride.is_joined || ride.is_pending
            );

            if (ridesToShow.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <p>🔍 Search for a route to view available rides.</p>
                    </div>
                `;
                return;
            }
        } else {
            if (ridesToShow.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <p>No rides found for this route.</p>
                    </div>
                `;
                return;
            }
        }

        ridesToShow.forEach(ride => {
            const card = document.createElement("div");
            card.classList.add("ride-card");

            if (ride.is_creator) {
                card.classList.add("pinned");
            }

            // ── Main action button ──
            let mainAction = "";

            if (ride.is_creator) {
                mainAction = `
                    <a class="delete-btn" href="#" onclick="confirmDelete('${ride.ride_id}'); return false;">
                        Delete
                    </a>
                `;
            } else if (ride.is_joined) {
                mainAction = `
                    <a class="leave-btn" href="#" onclick="openLeaveModal('${ride.ride_id}'); return false;">
                        Leave
                    </a>
                `;
            } else if (ride.is_pending) {
                mainAction = `
                    <span class="pending-badge">⏳ Pending Approval</span>
                    <a class="cancel-request-btn" href="#" onclick="cancelRequest('${ride.ride_id}'); return false;">
                        Cancel
                    </a>
                `;
            } else if (!ride.is_full) {
                mainAction = `
                    <a class="join-btn" href="#" onclick="requestJoin('${ride.ride_id}'); return false;">
                        Request to Join
                    </a>
                `;
            } else {
                mainAction = `<span style="color: var(--text-muted); font-style: italic;">Ride Full</span>`;
            }

            // ── Chat button (only for joined/creator) ──
            let chatButton = "";
            if (ride.is_joined || ride.is_creator) {
                chatButton = `
                    <button class="chat-btn" data-ride="${ride.ride_id}">
                        💬 Chat
                    </button>
                `;
            }

            // ── Pending requests section (only for creator) ──
            let pendingSection = "";
            if (ride.is_creator && ride.pending_requests_data && ride.pending_requests_data.length > 0) {
                const requestItems = ride.pending_requests_data.map(req => `
                    <div class="pending-request-item">
                        <span class="pending-request-name">👤 ${escapeHtml(req.name)}</span>
                        <div class="pending-request-actions">
                            <button class="approve-btn" onclick="approveRequest('${ride.ride_id}', '${encodeURIComponent(req.email)}', '${escapeHtml(req.name)}')">
                                ✓ Approve
                            </button>
                            <button class="reject-btn" onclick="rejectRequest('${ride.ride_id}', '${encodeURIComponent(req.email)}', '${escapeHtml(req.name)}')">
                                ✗ Reject
                            </button>
                        </div>
                    </div>
                `).join("");

                pendingSection = `
                    <div class="pending-requests-section">
                        <div class="pending-requests-header">
                            <span class="pending-requests-title">🔔 Join Requests</span>
                            <span class="pending-count-badge">${ride.pending_requests_data.length}</span>
                        </div>
                        <div class="pending-requests-list">
                            ${requestItems}
                        </div>
                    </div>
                `;
            }

            const seatsColor = ride.seats_available > 0 ? 'var(--success)' : 'var(--danger)';

            card.setAttribute("data-ride-id", ride.ride_id);
            card.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <h3 style="margin:0;">${ride.from} → ${ride.to}</h3>
                    <span id="safety-${ride.ride_id}" class="safety-badge" title="Loading safety score...">⏳</span>
                </div>
                <p><strong>Time:</strong> ${ride.time}</p>
                <p>
                    <strong>Available Seats:</strong>
                    <strong style="color: ${seatsColor}">
                        ${ride.seats_available}/${ride.seats_total}
                    </strong>
                </p>
                ${pendingSection}
                <div class="ride-actions">
                    ${mainAction}
                    ${chatButton}
                </div>
            `;

            container.appendChild(card);
        });
        loadAllSafetyScores();
/* ===================================================
   AI SAFETY RISK SCORER
=================================================== */

function loadAllSafetyScores() {
    document.querySelectorAll(".ride-card[data-ride-id]").forEach(card => {
        loadSafetyScore(card.dataset.rideId);
    });
}

async function loadSafetyScore(rideId) {
    const badge = document.getElementById(`safety-${rideId}`);
    if (!badge) return;

    try {
        const res  = await fetch(`/ai/safety_score/${rideId}`);
        const data = await res.json();

        if (data.error) { badge.textContent = ""; return; }

        const map = {
            low:      { label: "🟢 Safe",     color: "var(--success)" },
            moderate: { label: "🟡 Moderate",  color: "var(--warning)" },
            high:     { label: "🔴 High Risk", color: "var(--danger)"  }
        };

        const info = map[data.level] || { label: "🔵 Unknown", color: "var(--text-muted)" };
        badge.textContent  = `${info.label} ${data.confidence}%`;
        badge.style.color  = info.color;
        badge.title        = data.tip;
        badge.style.borderColor = info.color;

    } catch (e) {
        if (badge) badge.textContent = "";
    }
}


        attachChatButtonListeners();

    } catch (error) {
        console.error("Ride fetch error:", error);
        container.innerHTML = `
            <div class="empty-state">
                <p>Error loading rides. Please refresh the page.</p>
            </div>
        `;
    }
}

/* ===================================================
   RIDE ACTIONS
=================================================== */

// NEW: Send a join request (replaces direct join)
async function requestJoin(rideId) {
    try {
        const response = await fetch(`/request_join/${rideId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (response.ok) {
            await fetchRides();
            showNotification(data.message || 'Join request sent!', 'info');
        } else {
            showNotification(data.error || 'Failed to send request', 'error');
        }
    } catch (error) {
        console.error('Request join error:', error);
        showNotification('Error sending request. Please try again.', 'error');
    }
}

// NEW: Creator approves a join request
async function approveRequest(rideId, encodedEmail, name) {
    try {
        const response = await fetch(`/approve_request/${rideId}/${encodedEmail}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (response.ok) {
            await fetchRides();
            showNotification(data.message || `${name} approved!`, 'success');
        } else {
            showNotification(data.error || 'Failed to approve', 'error');
        }
    } catch (error) {
        console.error('Approve error:', error);
        showNotification('Error approving request. Please try again.', 'error');
    }
}

// NEW: Creator rejects a join request
async function rejectRequest(rideId, encodedEmail, name) {
    try {
        const response = await fetch(`/reject_request/${rideId}/${encodedEmail}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (response.ok) {
            await fetchRides();
            showNotification(data.message || `${name} rejected.`, 'info');
        } else {
            showNotification(data.error || 'Failed to reject', 'error');
        }
    } catch (error) {
        console.error('Reject error:', error);
        showNotification('Error rejecting request. Please try again.', 'error');
    }
}

// NEW: User cancels their own pending request
async function cancelRequest(rideId) {
    try {
        const response = await fetch(`/cancel_request/${rideId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (response.ok) {
            await fetchRides();
            showNotification('Request cancelled', 'info');
        } else {
            showNotification(data.error || 'Failed to cancel request', 'error');
        }
    } catch (error) {
        console.error('Cancel request error:', error);
        showNotification('Error cancelling request. Please try again.', 'error');
    }
}

/* ===================================================
   LEAVE MODAL (NEW: requires reason message)
=================================================== */

let leaveTargetRideId = null;

function initLeaveModal() {
    const modal = document.getElementById("leave-modal");
    if (!modal) return;

    // Close on overlay click
    modal.addEventListener("click", (e) => {
        if (e.target === modal) closeLeaveModal();
    });

    // Form submit
    const form = document.getElementById("leave-form");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const reason = document.getElementById("leave-reason").value.trim();

            if (!reason || reason.length < 5) {
                showLeaveError("Please write at least a short reason (5+ characters).");
                return;
            }

            await submitLeave(leaveTargetRideId, reason);
        });
    }
}

function openLeaveModal(rideId) {
    leaveTargetRideId = rideId;
    const modal = document.getElementById("leave-modal");
    if (!modal) return;

    // Reset form
    document.getElementById("leave-reason").value = "";
    clearLeaveError();

    modal.classList.remove("hidden");
    setTimeout(() => document.getElementById("leave-reason").focus(), 100);
}

function closeLeaveModal() {
    const modal = document.getElementById("leave-modal");
    if (modal) modal.classList.add("hidden");
    leaveTargetRideId = null;
}

function showLeaveError(msg) {
    const el = document.getElementById("leave-error");
    if (el) {
        el.textContent = msg;
        el.classList.remove("hidden");
    }
}

function clearLeaveError() {
    const el = document.getElementById("leave-error");
    if (el) {
        el.textContent = "";
        el.classList.add("hidden");
    }
}

async function submitLeave(rideId, reason) {
    const submitBtn = document.getElementById("leave-submit-btn");
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Leaving...";
    }

    try {
        const response = await fetch(`/leave/${rideId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason })
        });

        const data = await response.json();

        if (response.ok) {
            closeLeaveModal();
            await fetchRides();
            showNotification('You have left the ride', 'success');
        } else {
            showLeaveError(data.error || 'Failed to leave ride');
        }
    } catch (error) {
        console.error('Leave error:', error);
        showLeaveError('Error leaving ride. Please try again.');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Leave Ride";
        }
    }
}

/* ===================================================
   REQUEST MODALS / KEYBOARD HANDLING
=================================================== */

function initRequestModals() {
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeLeaveModal();
        }
    });
}

/* ===================================================
   DELETE
=================================================== */

async function confirmDelete(rideId) {
    if (!confirm('Are you sure you want to delete this ride?')) return;

    try {
        const response = await fetch(`/delete/${rideId}`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (response.ok) {
            await fetchRides();
            showNotification('Ride deleted successfully', 'success');
        } else {
            const error = await response.text();
            showNotification(error || 'Failed to delete ride', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showNotification('Error deleting ride. Please try again.', 'error');
    }
}

/* ===================================================
   NOTIFICATION SYSTEM
=================================================== */

function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/* ===================================================
   CHAT SYSTEM
=================================================== */

function initChatSystem() {
    const chatForm = document.getElementById("chat-form");
    if (!chatForm) return;

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!currentRideId) return;

        const input = document.getElementById("chat-input");
        const message = input.value.trim();
        if (!message) return;

        try {
            await fetch(`/chat/send/${currentRideId}`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `message=${encodeURIComponent(message)}`
            });

            input.value = "";
            loadChat();
        } catch (error) {
            console.error("Chat send error:", error);
            showNotification('Failed to send message', 'error');
        }
    });
}

function attachChatButtonListeners() {
    const buttons = document.querySelectorAll(".chat-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const rideId = btn.getAttribute("data-ride");
            openChat(rideId);
        });
    });
}

function openChat(rideId) {
    currentRideId = rideId;
    const modal = document.getElementById("chat-modal");
    if (!modal) return;

    modal.classList.remove("hidden");
    loadChat();

    if (chatInterval) clearInterval(chatInterval);
    chatInterval = setInterval(loadChat, 3000);
}

function closeChat() {
    const modal = document.getElementById("chat-modal");
    if (!modal) return;

    modal.classList.add("hidden");
    currentRideId = null;

    if (chatInterval) {
        clearInterval(chatInterval);
        chatInterval = null;
    }
}

async function loadChat() {
    if (!currentRideId) return;

    try {
        const response = await fetch(`/chat/${currentRideId}`);
        const messages = await response.json();

        const container = document.getElementById("chat-messages");
        if (!container) return;

        const currentUser = document.body.dataset.username;
        const wasAtBottom = container.scrollHeight - container.scrollTop === container.clientHeight;

        container.innerHTML = "";

        messages.forEach(msg => {
            const div = document.createElement("div");

            // System messages (leave notices etc.)
            if (msg.is_system) {
                div.classList.add("message", "system-message");
                div.innerHTML = `<span>${escapeHtml(msg.text)}</span>`;
            } else {
                div.classList.add("message");
                if (msg.user === currentUser) {
                    div.classList.add("mine");
                } else {
                    div.classList.add("other");
                }
                div.innerHTML = `
                    <strong style="font-size: 0.75rem; opacity: 0.7;">${msg.user}</strong>
                    <div style="margin: 4px 0;">${escapeHtml(msg.text)}</div>
                    <small style="opacity: 0.5; font-size: 0.7rem;">${msg.time}</small>
                `;
            }

            container.appendChild(div);
        });

        if (wasAtBottom || messages.length <= 1) {
            container.scrollTop = container.scrollHeight;
        }

    } catch (error) {
        console.error("Chat load error:", error);
    }
}

/* ===================================================
   SEARCH FUNCTIONALITY
=================================================== */

function searchRides() {
    const from = document.getElementById("fromInput").value.trim();
    const to = document.getElementById("toInput").value.trim();

    if (!from && !to) {
        showNotification('Please enter at least one location', 'error');
        return;
    }

    let query = "/rides?";
    if (from) query += `from=${encodeURIComponent(from)}&`;
    if (to) query += `to=${encodeURIComponent(to)}`;

    window.location.href = query;
}

/* ===================================================
   UTILITY FUNCTIONS
=================================================== */

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/* ===================================================
   CLEANUP ON PAGE UNLOAD
=================================================== */

window.addEventListener('beforeunload', () => {
    if (rideInterval) clearInterval(rideInterval);
    if (chatInterval) clearInterval(chatInterval);
});