document.addEventListener("DOMContentLoaded", function () {

    console.log("course_admission.js loaded");

    const courseSelect = document.getElementById("course");
    const contentBox = document.getElementById("courseContentBox");
    const durationInput = document.getElementById("duration");
    const totalFeesInput = document.getElementById("total_fees");
    const discountedFeesInput = document.querySelector("input[name='discounted_fees']");

    /* ================= GET CONTENTS FROM URL ================= */

    const urlParams = new URLSearchParams(window.location.search);

    const selectedContents = urlParams.get("course_content")
        ? urlParams.get("course_content").split(",").map(x => x.trim())
        : [];

    /* ================= LOAD COURSE CONTENTS ================= */

    function loadCourseContents(courseId){

        if (!courseId) {
            contentBox.innerHTML = "<small>Select course first</small>";
            return;
        }

        fetch(`/ajax/course-contents/?course_id=${courseId}`)
        .then(res => res.json())
        .then(data => {

            contentBox.innerHTML = "";

            if(data.length === 0){
                contentBox.innerHTML = "<small>No course contents available</small>";
                return;
            }

            data.forEach(item => {

                let checked = selectedContents.includes(item.name) ? "checked" : "";

                contentBox.innerHTML += `
                    <label class="content-check">
                        <input type="checkbox" name="course_content[]" value="${item.name}" ${checked}>
                        ${item.name}
                    </label>
                `;
            });

        })
        .catch(error => {
            console.error("Error loading course contents:", error);
        });

    }

    /* ================= COURSE CHANGE ================= */

    courseSelect.addEventListener("change", function(){

        const selectedOption = this.options[this.selectedIndex];
        const courseId = this.value;

        /* ---------- AUTO FILL ---------- */

        if(durationInput){
            durationInput.value = selectedOption.dataset.duration || "";
        }

        if(totalFeesInput){
            totalFeesInput.value = selectedOption.dataset.fees || "";
        }

        if(discountedFeesInput){
            discountedFeesInput.value = "";
        }

        /* ---------- LOAD CONTENT ---------- */

        loadCourseContents(courseId);

    });

    /* ================= AUTO LOAD ON PAGE LOAD ================= */

    if(courseSelect.value){
        const selectedOption = courseSelect.options[courseSelect.selectedIndex];

        if(durationInput){
            durationInput.value = selectedOption.dataset.duration || "";
        }

        if(totalFeesInput){
            totalFeesInput.value = selectedOption.dataset.fees || "";
        }

        loadCourseContents(courseSelect.value);
    }

});