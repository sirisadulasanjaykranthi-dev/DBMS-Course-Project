/* ============================================================
   Solar Installation & Maintenance Service Management System
   Client-Side Interactive Helpers & Confirmation Handlers
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Setup Generic Delete Confirmation Modal
  const deleteModalEl = document.getElementById("deleteConfirmModal");
  if (deleteModalEl) {
    deleteModalEl.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const deleteUrl = button.getAttribute("data-delete-url");
      const itemName = button.getAttribute("data-item-name") || "this record";
      const itemId = button.getAttribute("data-item-id") || "";

      const formEl = document.getElementById("deleteModalForm");
      const nameEl = document.getElementById("deleteModalItemName");
      const idEl = document.getElementById("deleteModalItemId");

      if (formEl && deleteUrl) formEl.action = deleteUrl;
      if (nameEl) nameEl.textContent = itemName;
      if (idEl) idEl.textContent = itemId ? `(ID: ${itemId})` : "";
    });
  }

  // 2. Client-side Real-time Search filter for table lists
  const tableSearchInput = document.getElementById("clientTableSearch");
  if (tableSearchInput) {
    tableSearchInput.addEventListener("keyup", function () {
      const query = this.value.toLowerCase();
      const rows = document.querySelectorAll(".data-search-row");

      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.style.display = text.indexOf(query) > -1 ? "" : "none";
      });
    });
  }

  // 3. Auto-dismiss Alert banners after 6 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    });
  }, 6000);
});
