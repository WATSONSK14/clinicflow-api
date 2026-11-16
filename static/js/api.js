// static/js/api.js - Central API & Toast Layer

const API_BASE = "";

// Toast Notification Engine (Z-Index 9999 ensures visibility above modals)
function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    
    toast.innerText = message;
    toast.className = `fixed top-5 right-5 z-[9999] p-4 rounded-xl shadow-2xl text-white font-medium transition-all transform duration-300 ${
        isError ? "bg-rose-500 shadow-rose-500/20" : "bg-emerald-500 shadow-emerald-500/20"
    }`;
    toast.classList.remove("hidden");
    
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}

// Token Storage Helpers
function getToken() {
    return localStorage.getItem("clinicflow_token");
}

function setToken(token) {
    localStorage.setItem("clinicflow_token", token);
}

function removeToken() {
    localStorage.removeItem("clinicflow_token");
}

// Standardized Fetch Wrapper
async function apiFetch(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = getToken();

    if (token && !headers["Authorization"]) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            if (response.status === 401) {
                // If unauthorized, clean stale token
                removeToken();
                if (typeof updateAuthUI === "function") {
                    updateAuthUI(null);
                }
            }
            const errorMsg = data?.detail || `İşlem başarısız oldu (${response.status})`;
            throw new Error(errorMsg);
        }

        return data;
    } catch (err) {
        throw err;
    }
}
