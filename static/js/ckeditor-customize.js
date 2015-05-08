function attach_ckeditor(attach_to){
    CKEDITOR.replace(attach_to,{
		toolbar: [
			[ 'Undo','Redo','-','Bold','Italic','Link','Unlink','Subscript','Superscript','Strike','-','BulletedList','NumberedList','Blockquote','Image','-','Format','-', 'Source'],
		]
	});
}
