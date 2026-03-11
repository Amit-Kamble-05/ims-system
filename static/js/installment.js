document.addEventListener("DOMContentLoaded", function () {

    const tableBody = document.getElementById("installmentBody");
    const addBtn = document.getElementById("addInstallment");
    const totalSpan = document.getElementById("installmentTotal");
    const remainingSpan = document.getElementById("remainingBalance");
    const discountedInput = document.querySelector("[name='discounted_fees']");

    function today() {
        return new Date().toISOString().split("T")[0];
    }

        /* ---------- NEXT INSTALLMENT INDEX ---------- */
    function getNextInstallmentIndex() {
        return document.querySelectorAll(".dynamic-row").length + 1;
    }

    /* ---------- ADD INSTALLMENT ---------- */
    function addInstallmentRow() {
        const index = getNextInstallmentIndex();

        const row = document.createElement("tr");
        row.classList.add("installment-row", "dynamic-row");

        row.innerHTML = `
            <td>
                <input name="installment_type[]" class="form-control" value="Installment-${index}" readonly>
            </td>
            <td>
                <input type="date" name="installment_date[]" class="form-control" required>
            </td>
            <td>
                <input name="installment_amount[]" class="form-control installment-amount" placeholder="Amount" required>
            </td>
            <td>
                <button type="button"
                        class="btn btn-sm btn-danger remove-row">
                    ✖
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    }

    /* ---------- TOTAL & REMAINING (CORRECT LOGIC) ---------- */
    function calculateTotals() {

        // Do not recalculate in EDIT MODE
        if (typeof EDIT_MODE !== "undefined" && EDIT_MODE) {
            return;
        }

        let totalInstallmentAmount = 0;

        document.querySelectorAll(".installment-amount").forEach(input => {
            totalInstallmentAmount += parseFloat(input.value || 0);
        });

        // Total installments (includes registration fee)
        totalSpan.innerText = totalInstallmentAmount.toFixed(2);

        const discountedFees = parseFloat(discountedInput.value || 0);

        // Registration fee already included → subtract once
        const remaining = discountedFees - (totalInstallmentAmount-100);

        remainingSpan.innerText = remaining.toFixed(2);
    }

    /* ---------- LIVE CALCULATION ---------- */
    tableBody.addEventListener("input", function (e) {
        if (e.target.classList.contains("installment-amount")) {
            calculateTotals();
        }
    });

    discountedInput.addEventListener("input", calculateTotals);

    /* ---------- REMOVE INSTALLMENT ---------- */
    tableBody.addEventListener("click", function (e) {
        if (e.target.classList.contains("remove-row")) {
            e.target.closest("tr").remove();
            calculateTotals();
        }
    });

    if (addBtn) {
        addBtn.addEventListener("click", addInstallmentRow);
    }

    document.querySelector("form").addEventListener("submit", function (e) {

        calculateTotals();

        const totalInstallments =
            parseFloat(totalSpan.innerText || 0) - 100; // exclude registration

        const discountedFees = parseFloat(discountedInput.value || 0);

        if (totalInstallments > discountedFees) {
            alert("Installment total cannot exceed discounted fees");
            e.preventDefault();
        }
        else if (totalInstallments < discountedFees) {
            alert("Installment total cannot exceed discounted fees");
            e.preventDefault();
        }
    });

    calculateTotals();
});
