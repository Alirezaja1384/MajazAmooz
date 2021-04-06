tinymce.init({
    selector: 'textarea.tinymce',
    directionality : 'rtl',
    language: 'fa',

    toolbar: 'undo redo | forecolor | bold italic | alignleft aligncenter alignright alignjustify',
    setup: function (editor) {
        editor.on('change', function (e) {
            editor.save();
        });
    }
});
