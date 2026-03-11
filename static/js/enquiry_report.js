const searchInput = document.getElementById("searchInput");
const statusFilter = document.getElementById("statusFilter");
const fromDate = document.getElementById("fromDate");
const toDate = document.getElementById("toDate");
const clearBtn = document.getElementById("clearFilters");

function filterTable() {

    const rows = document.querySelectorAll("#enquiryTable tbody tr");

    const search = searchInput.value.toLowerCase();
    const status = statusFilter.value.toLowerCase();
    const from = fromDate.value ? new Date(fromDate.value) : null;
    const to = toDate.value ? new Date(toDate.value) : null;

    rows.forEach(row => {

        // IMPORTANT → always reset first
        row.style.display = "";

        const rowText = row.innerText.toLowerCase();
        const rowStatus = row.querySelector(".status").innerText.toLowerCase();
        const dateText = row.cells[1].innerText.trim();

        const rowDate = new Date(dateText);

        let visible = true;

        // SEARCH FILTER
        if (search && !rowText.includes(search)) {
            visible = false;
        }

        // STATUS FILTER
        if (status && rowStatus !== status) {
            visible = false;
        }

        // SINGLE DATE
        if (from && !to) {
            if (rowDate.toDateString() !== from.toDateString()) {
                visible = false;
            }
        }

        // DATE RANGE
        if (from && to) {
            if (rowDate < from || rowDate > to) {
                visible = false;
            }
        }

        row.style.display = visible ? "" : "none";

    });
// RESET BUTTON

clearBtn.addEventListener("click", () => {

    searchInput.value = "";
    statusFilter.value = "";
    fromDate.value = "";
    toDate.value = "";

    rows.forEach(row => {
        row.style.display = "";
    });

});
    
}


searchInput.addEventListener("keyup", filterTable);
statusFilter.addEventListener("change", filterTable);
fromDate.addEventListener("change", filterTable);
toDate.addEventListener("change", filterTable);

