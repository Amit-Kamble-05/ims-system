document.addEventListener("DOMContentLoaded", function () {

    console.log("students.js loaded");

    const actionBar = document.getElementById("actionBar");
    const checkboxes = document.querySelectorAll(".student-check");
    const selectAll = document.getElementById("selectAll");

    const btnEdit = document.getElementById("btnEdit");
    const btnView = document.getElementById("btnView");
    const btnDelete = document.getElementById("btnDelete");

    function updateActionBar() {
        const selected = Array.from(checkboxes).filter(cb => cb.checked);

        if (selected.length >= 1) {
            actionBar.classList.remove("d-none");

            const studentId = selected[0].dataset.studentId;
            const admissionId = selected[0].dataset.admissionId;

            btnEdit.href = `/students/edit/${studentId}/`;
            btnDelete.href = `/students/delete/${studentId}/`;

            if (admissionId) {
                btnView.href = `/admission/detail/${admissionId}/`;
            } else {
                btnView.href = "#";
                btnView.onclick = function () {
                    alert("Admission not completed for this student");
                    return false;
                };
            }

        } else {
            actionBar.classList.add("d-none");
        }
    }

    checkboxes.forEach(cb => {
        cb.addEventListener("change", updateActionBar);
    });

    if (selectAll) {
        selectAll.addEventListener("change", function () {
            checkboxes.forEach(cb => cb.checked = this.checked);
            updateActionBar();
        });
    }
});
