// static/js/auth.js - Authentication & User State Engine

let currentUser = null;

function openAuthModal(tab = "login") {
    setAuthTab(tab);
    document.getElementById("auth-modal").classList.remove("hidden");
}

function closeAuthModal() {
    document.getElementById("auth-modal").classList.add("hidden");
    document.getElementById("login-form").reset();
    document.getElementById("register-form").reset();
}

function setAuthTab(tab) {
    const isLogin = tab === "login";
    document.getElementById("login-form").classList.toggle("hidden", !isLogin);
    document.getElementById("register-form").classList.toggle("hidden", isLogin);

    document.getElementById("auth-tab-login").className = isLogin
        ? "flex-1 py-2 font-bold text-sm text-primary border-b-2 border-primary"
        : "flex-1 py-2 font-bold text-sm text-slate-400 hover:text-slate-600";

    document.getElementById("auth-tab-register").className = !isLogin
        ? "flex-1 py-2 font-bold text-sm text-accent border-b-2 border-accent"
        : "flex-1 py-2 font-bold text-sm text-slate-400 hover:text-slate-600";
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    try {
        const data = await apiFetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData.toString()
        });

        setToken(data.access_token);
        showToast("Giriş başarılı! Hoş geldiniz.");
        closeAuthModal();
        await checkAuthStatus();

        if (typeof loadAppointments === "function") {
            loadAppointments();
        }
    } catch (err) {
        showToast(err.message, true);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const full_name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const phone_number = document.getElementById("reg-phone").value.trim();
    const password = document.getElementById("reg-password").value;

    try {
        await apiFetch("/auth/register", {
            method: "POST",
            body: JSON.stringify({ full_name, email, phone_number, password })
        });

        showToast("Kayıt başarılı! Şimdi giriş yapabilirsiniz.");
        setAuthTab("login");
        document.getElementById("login-email").value = email;
        document.getElementById("login-password").focus();
    } catch (err) {
        showToast(err.message, true);
    }
}

function handleLogout() {
    removeToken();
    currentUser = null;
    updateAuthUI(null);
    showToast("Başarıyla çıkış yapıldı.");
    if (typeof switchTab === "function") {
        switchTab("doctors");
    }
}

function updateAuthUI(user) {
    const userArea = document.getElementById("user-area");
    if (!userArea) return;

    if (user) {
        userArea.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="flex items-center space-x-2 bg-sky-50 border border-sky-100 px-3 py-1.5 rounded-xl">
                    <div class="w-7 h-7 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold shadow-sm">
                        ${user.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
                    </div>
                    <div class="text-left hidden sm:block">
                        <span class="block text-xs font-bold text-slate-800 leading-none">${user.full_name}</span>
                        <span class="text-[10px] text-sky-600 font-semibold uppercase tracking-wider">${user.role}</span>
                    </div>
                </div>
                <button onclick="handleLogout()" title="Çıkış Yap" class="text-slate-400 hover:text-rose-500 p-2 rounded-lg hover:bg-slate-100 transition">
                    <i class="fa-solid fa-arrow-right-from-bracket"></i>
                </button>
            </div>
        `;
    } else {
        userArea.innerHTML = `
            <button onclick="openAuthModal('login')" class="bg-primary hover:bg-sky-700 text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-sm hover:shadow transition flex items-center space-x-1.5">
                <i class="fa-solid fa-right-to-bracket text-xs"></i>
                <span>Giriş Yap</span>
            </button>
        `;
    }
}

async function checkAuthStatus() {
    const token = getToken();
    if (!token) {
        currentUser = null;
        updateAuthUI(null);
        return;
    }

    try {
        const user = await apiFetch("/auth/me");
        currentUser = user;
        updateAuthUI(user);
    } catch (err) {
        currentUser = null;
        updateAuthUI(null);
    }
}
