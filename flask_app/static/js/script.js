document.getElementById('file-upload').addEventListener('change', function() {
    var file = this.files[0];
    var fileType = file.type.split('/')[0];
    if (fileType !== 'image') {
        alert('Please select an image file.');
        this.value = '';
    }
});