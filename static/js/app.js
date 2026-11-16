// XSS Protection Helper (Sanitizes user inputs against HTML/script injection)
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
// static/js/app.js - Main Application Logic & Booking Engine

let allDoctors = [];
let selectedDoctor = null;
let selectedSlotId = null;

// Tab Navigation
function switchTab(tab) {
    const sectionDoctors = document.getElementById("section-doctors");
    const sectionAppointments = document.getElementById("section-appointments");
    const btnDoctors = document.getElementById("tab-doctors-btn");
    const btnAppointments = document.getElementById("tab-app-btn");

    const mBtnDoctors = document.getElementById("mobile-tab-doctors-btn");
    const mBtnAppointments = document.getElementById("mobile-tab-app-btn");

    if (tab === "doctors") {
        sectionDoctors.classList.remove("hidden");
        sectionAppointments.classList.add("hidden");
        if (btnDoctors) btnDoctors.className = "nav-btn px-3 py-2 rounded-xl text-sm font-bold text-primary bg-sky-50";
        if (btnAppointments) btnAppointments.className = "nav-btn px-3 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:text-primary transition";
        if (mBtnDoctors) mBtnDoctors.className = "flex-1 py-2 rounded-xl text-xs font-bold text-primary bg-sky-50 flex items-center justify-center space-x-1.5";
        if (mBtnAppointments) mBtnAppointments.className = "flex-1 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-primary bg-slate-50 flex items-center justify-center space-x-1.5";
    } else {
        if (!currentUser) {
            showToast("Randevularınızı görmek için lütfen önce giriş yapınız!", true);
            openAuthModal("login");
            return;
        }
        sectionDoctors.classList.add("hidden");
        sectionAppointments.classList.remove("hidden");
        if (btnDoctors) btnDoctors.className = "nav-btn px-3 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:text-primary transition";
        if (btnAppointments) btnAppointments.className = "nav-btn px-3 py-2 rounded-xl text-sm font-bold text-primary bg-sky-50";
        if (mBtnDoctors) mBtnDoctors.className = "flex-1 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-primary bg-slate-50 flex items-center justify-center space-x-1.5";
        if (mBtnAppointments) mBtnAppointments.className = "flex-1 py-2 rounded-xl text-xs font-bold text-primary bg-sky-50 flex items-center justify-center space-x-1.5";
        loadAppointments();
    }
}

// -------------------------------------------------------------
// DOKTOR YÖNETİMİ & ARAMA
// -------------------------------------------------------------
async function loadDoctors() {
    const grid = document.getElementById("doctors-grid");
    try {
        const doctors = await apiFetch("/doctors/");
        allDoctors = doctors;
        renderDoctorCards(doctors);
    } catch (err) {
        grid.innerHTML = `
            <div class="col-span-full text-center py-12 text-rose-500">
                <i class="fa-solid fa-triangle-exclamation text-3xl mb-3"></i>
                <p>Doktor listesi yüklenirken bir hata oluştu: ${err.message}</p>
            </div>
        `;
    }
}

function filterDoctors() {
    const query = document.getElementById("specialty-filter").value.trim().toLowerCase();
    const filtered = allDoctors.filter(d => {
        const specialtyMatch = d.specialty?.toLowerCase().includes(query);
        const nameMatch = d.user?.full_name?.toLowerCase().includes(query);
        return specialtyMatch || nameMatch;
    });
    renderDoctorCards(filtered);
}

function renderDoctorCards(doctors) {
    const grid = document.getElementById("doctors-grid");
    if (!doctors || doctors.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full text-center py-12 text-slate-400">
                <i class="fa-regular fa-face-frown text-3xl mb-3"></i>
                <p class="font-medium">Aramanızla eşleşen doktor bulunamadı.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = doctors.map(d => {
        const docName = d.user?.full_name || "Dr. Hekim";
        return `
            <div class="doctor-card bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between">
                <div>
                    <div class="flex items-start justify-between">
                        <div class="flex items-center space-x-3.5">
                            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-500 to-primary flex items-center justify-center text-white text-xl shadow-md shadow-sky-500/20">
                                <i class="fa-solid fa-user-doctor"></i>
                            </div>
                            <div>
                                <h3 class="font-bold text-slate-800 text-base leading-tight">${escapeHtml(docName)}</h3>
                                <span class="inline-block mt-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-sky-50 text-sky-700 border border-sky-100">
                                    ${d.specialty}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="mt-5 space-y-2 text-xs font-medium text-slate-500 border-t border-slate-100 pt-4">
                        <div class="flex items-center justify-between">
                            <span class="flex items-center"><i class="fa-solid fa-door-open w-4 text-slate-400 mr-1.5"></i> Poliklinik / Oda</span>
                            <span class="font-bold text-slate-700">${d.room_number || "Ana Bina"}</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="flex items-center"><i class="fa-regular fa-clock w-4 text-slate-400 mr-1.5"></i> Çalışma Saatleri</span>
                            <span class="font-bold text-slate-700">${d.working_start} - ${d.working_end}</span>
                        </div>
                    </div>
                </div>

                <button onclick="openBookingModal(${d.id}, '${escapeHtml(docName)}', '${d.specialty}', '${d.room_number}', '${d.working_start}', '${d.working_end}')"
                    class="mt-6 w-full py-2.5 bg-gradient-to-r from-primary to-secondary hover:from-sky-700 hover:to-primary text-white text-sm font-bold rounded-xl shadow-md shadow-sky-500/20 hover:shadow-lg transition flex items-center justify-center space-x-2">
                    <i class="fa-regular fa-calendar-check"></i>
                    <span>Randevu Al</span>
                </button>
            </div>
        `;
    }).join("");
}

// -------------------------------------------------------------
// RANDEVU ALMA & DİNAMİK SLOT MOTORU (MHRS KONSEPTİ)
// -------------------------------------------------------------
function openBookingModal(doctorId, doctorName, specialty, room, start, end) {
    if (!currentUser) {
        showToast("Randevu alabilmek için lütfen önce giriş yapınız!", true);
        openAuthModal("login");
        return;
    }

    selectedDoctor = { id: doctorId, name: doctorName, specialty, room, start, end };
    selectedSlotId = null;

    document.getElementById("book-doctor-id").value = doctorId;
    document.getElementById("book-slot-id").value = "";
    document.getElementById("book-doctor-name").innerHTML = `
        <span class="font-bold text-slate-800">${doctorName}</span>
        <span class="text-xs text-sky-600 block">${specialty} (${start} - ${end})</span>
    `;

    // Varsayılan olarak bugünün tarihini seç ve minimum tarihi bugün yap
    const today = new Date().toISOString().split("T")[0];
    const dateInput = document.getElementById("book-date");
    dateInput.min = today;
    dateInput.value = today;

    document.getElementById("booking-modal").classList.remove("hidden");
    loadDoctorSlots();
}

function closeBookingModal() {
    document.getElementById("booking-modal").classList.add("hidden");
    document.getElementById("booking-form").reset();
    selectedDoctor = null;
    selectedSlotId = null;
}

async function loadDoctorSlots() {
    const doctorId = document.getElementById("book-doctor-id").value;
    const dateVal = document.getElementById("book-date").value;
    const container = document.getElementById("slots-container");

    if (!dateVal) {
        container.innerHTML = `<div class="col-span-2 text-center text-xs text-slate-400 py-4">Lütfen geçerli bir tarih seçiniz.</div>`;
        return;
    }

    container.innerHTML = `
        <div class="col-span-2 text-center text-xs text-slate-400 py-4">
            <i class="fa-solid fa-spinner fa-spin mr-1"></i> Müsait saatler kontrol ediliyor...
        </div>
    `;

    try {
        const slots = await apiFetch(`/doctors/${doctorId}/available-slots?appointment_date=${dateVal}`);
        
        if (!slots || slots.length === 0) {
            container.innerHTML = `<div class="col-span-2 text-center text-xs text-slate-400 py-4">Bu tarihte uygun randevu saati bulunmuyor.</div>`;
            return;
        }

        container.innerHTML = slots.map(s => {
            const isAvail = s.is_available;
            if (isAvail) {
                return `
                    <button type="button" onclick="selectSlot(${s.id}, this)"
                        class="slot-btn p-2 rounded-lg text-xs font-bold border border-emerald-200 bg-emerald-50/80 text-emerald-800 hover:bg-emerald-500 hover:text-white hover:border-emerald-500 transition flex items-center justify-between">
                        <span>${s.start_time} - ${s.end_time}</span>
                        <i class="fa-regular fa-circle-check text-emerald-600"></i>
                    </button>
                `;
            } else {
                return `
                    <div class="p-2 rounded-lg text-xs font-semibold border border-rose-200 bg-rose-50/60 text-rose-400 flex items-center justify-between cursor-not-allowed opacity-75">
                        <span class="line-through">${s.start_time} - ${s.end_time}</span>
                        <i class="fa-solid fa-lock text-rose-300"></i>
                    </div>
                `;
            }
        }).join("");

    } catch (err) {
        container.innerHTML = `<div class="col-span-2 text-center text-xs text-rose-500 py-4">${err.message}</div>`;
    }
}

function selectSlot(slotId, element) {
    selectedSlotId = slotId;
    document.getElementById("book-slot-id").value = slotId;

    // Reset previous selection highlights
    document.querySelectorAll(".slot-btn").forEach(btn => {
        btn.classList.remove("bg-emerald-600", "text-white", "ring-2", "ring-emerald-400");
    });

    // Highlight selected slot
    element.classList.add("bg-emerald-600", "text-white", "ring-2", "ring-emerald-400");
}

async function handleBookAppointment(e) {
    e.preventDefault();
    const doctor_id = parseInt(document.getElementById("book-doctor-id").value);
    const appointment_date = document.getElementById("book-date").value;
    const slot_id = parseInt(document.getElementById("book-slot-id").value);
    const notes = document.getElementById("book-notes").value.trim();

    if (!slot_id) {
        showToast("Lütfen yeşil renkli boş saat dilimlerinden birini seçiniz!", true);
        return;
    }

    try {
        await apiFetch("/appointments/", {
            method: "POST",
            body: JSON.stringify({
                doctor_id,
                appointment_date,
                slot_id,
                notes: notes || null
            })
        });

        showToast("Randevunuz başarıyla oluşturuldu! Geçmiş olsun.");
        closeBookingModal();
        switchTab("appointments");
    } catch (err) {
        showToast(err.message, true);
    }
}

// -------------------------------------------------------------
// RANDEVULARIM TABLOSU & İPTAL
// -------------------------------------------------------------
async function loadAppointments() {
    const tbody = document.getElementById("appointments-tbody");
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center py-8 text-slate-400">
                <i class="fa-solid fa-spinner fa-spin mr-1"></i> Randevularınız getiriliyor...
            </td>
        </tr>
    `;

    try {
        const appointments = await apiFetch("/appointments/");
        renderAppointments(appointments);
    } catch (err) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-8 text-rose-500 font-medium">
                    Randevular yüklenirken hata oluştu: ${err.message}
                </td>
            </tr>
        `;
    }
}

function renderAppointments(list) {
    const tbody = document.getElementById("appointments-tbody");
    if (!list || list.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-12 text-slate-400">
                    <i class="fa-regular fa-calendar-xmark text-3xl mb-2 block"></i>
                    Kayıtlı herhangi bir randevunuz bulunmamaktadır.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = list.map(app => {
        const isScheduled = app.status === "scheduled";
        const isCompleted = app.status === "completed";
        const isCancelled = app.status === "cancelled";

        let statusBadge = "";
        if (isScheduled) {
            statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Aktif</span>`;
        } else if (isCompleted) {
            statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-sky-50 text-sky-700 border border-sky-200">Tamamlandı</span>`;
        } else {
            statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-500 border border-slate-200">İptal Edildi</span>`;
        }

        const docName = app.doctor?.user?.full_name || "Dr. Hekim";
        const specialty = app.doctor?.specialty || "";
        const patientName = app.patient?.full_name || currentUser?.full_name || "-";

        return `
            <tr class="hover:bg-slate-50/80 transition">
                <td class="p-4 font-bold text-slate-700 whitespace-nowrap">${app.appointment_date}</td>
                <td class="p-4 font-semibold text-slate-600 whitespace-nowrap">${app.start_time} - ${app.end_time}</td>
                <td class="p-4 whitespace-nowrap">
                    <div class="font-bold text-slate-800">${escapeHtml(docName)}</div>
                    <div class="text-xs text-slate-400 font-medium">${specialty}</div>
                </td>
                <td class="p-4 text-slate-600 whitespace-nowrap">${escapeHtml(patientName)}</td>
                <td class="p-4 text-xs text-slate-500 max-w-xs truncate">${escapeHtml(app.notes) || "-"}</td>
                <td class="p-4 whitespace-nowrap">${statusBadge}</td>
                <td class="p-4 text-right whitespace-nowrap">
                    ${isScheduled ? `
                        <button onclick="cancelAppointment(${app.id})" 
                            class="text-rose-600 hover:text-rose-800 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-lg text-xs font-bold transition">
                            <i class="fa-solid fa-ban mr-1"></i> İptal Et
                        </button>
                    ` : `<span class="text-xs text-slate-300 font-medium">-</span>`}
                </td>
            </tr>
        `;
    }).join("");
}

async function cancelAppointment(appointmentId) {
    if (!confirm("Bu randevuyu iptal etmek istediğinize emin misiniz?")) {
        return;
    }

    try {
        await apiFetch(`/appointments/${appointmentId}/cancel`, {
            method: "PATCH"
        });
        showToast("Randevunuz başarıyla iptal edildi.");
        loadAppointments();
    } catch (err) {
        showToast(err.message, true);
    }
}

// -------------------------------------------------------------
// SAYFA YÜKLENDİĞİNDE BAŞLATMA
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
    await checkAuthStatus();
    loadDoctors();
});


