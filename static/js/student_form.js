const photoInput = document.getElementById('photoInput');
const photoPreview = document.getElementById('photoPreview');

photoInput.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
        photoPreview.src = reader.result;
    };
    reader.readAsDataURL(file);
});
