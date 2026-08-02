/**
 * Admin Panel Core JavaScript Utilities
 */

document.addEventListener('DOMContentLoaded', function () {
    // Sidebar Toggle Handler
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('admin-sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alertList = document.querySelectorAll('.admin-auto-alert');
    alertList.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

/**
 * Toast Notification Helper
 * @param {string} message 
 * @param {string} type - 'success', 'danger', 'warning', 'info'
 */
function showAdminToast(message, type = 'info') {
    const toastContainer = document.getElementById('admin-toast-container');
    if (!toastContainer) return;

    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'danger' ? 'bg-danger' : type === 'warning' ? 'bg-warning text-dark' : 'bg-primary';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body font-weight-bold">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

/**
 * Loading Spinner Toggle Helpers
 */
function showAdminSpinner() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('active');
}

function hideAdminSpinner() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

/**
 * Action Confirmation Modal Trigger Helper
 */
function triggerAdminConfirm(title, message, confirmBtnClass, confirmText, onConfirmCallback) {
    const modalTitle = document.getElementById('adminConfirmModalLabel');
    const modalBody = document.getElementById('adminConfirmModalBody');
    const confirmBtn = document.getElementById('adminConfirmModalBtn');
    
    if (!modalTitle || !modalBody || !confirmBtn) return;

    modalTitle.innerText = title;
    modalBody.innerHTML = message;
    confirmBtn.className = 'btn ' + (confirmBtnClass || 'btn-primary');
    confirmBtn.innerText = confirmText || 'Confirm';

    // Remove previous listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

    newConfirmBtn.addEventListener('click', function () {
        const modalEl = document.getElementById('adminConfirmModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        if (typeof onConfirmCallback === 'function') {
            onConfirmCallback();
        }
    });

    const modal = new bootstrap.Modal(document.getElementById('adminConfirmModal'));
    modal.show();
}
