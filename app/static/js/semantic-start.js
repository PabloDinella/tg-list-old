$('.ui.dropdown')
	.dropdown()
;

$('select.dropdown')
  .dropdown()
;

$('.edit-card')
  .popup()
;

$('.ui.checkbox')
  .checkbox()
;

$('.message .close')
  .on('click', function() {
    $(this)
      .closest('.message')
      .transition('fade')
    ;
  })
;
