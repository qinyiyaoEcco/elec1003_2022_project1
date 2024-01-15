
/* Submit letter | Try Letter button form submit event */
function choseLetter(letter, num) {
  // get time and letter by user
  letter = 'letter' + '=' + letter;
  time = $('.stop-watch').text()

  // send a POST request when a user click on a letter button
  // json with letter and time data
  $.ajax({
    type: "POST",
    url: '',
    data: {"letter": letter, "time": time},
    success: function(data) {
      /* Refresh if finished */
      if (data.finished) {
        location.reload();
      }
      else {
        /* Update current */
        if (!data.repeat) {
          $('#current').text(data.current);

          /* Update errors */
          $('#errors').html(
            'Errors (' + data.errors.length + '/6): ' +
            '<span class="text-danger spaced">' + data.errors + '</span>');

          if (!data.correct) {
            // if not correct, then change bg to red color
            $('.letter-box')[num].style.background = '#ffcccb';
          } else {
            // if correct, then change bg to green color
            $('.letter-box')[num].style.background = 'lightgreen';
          }
          /* Update drawing */
          updateDrawing(data.errors);
        }
      }
    }
  });
}

function updateDrawing(errors) {
  // based on how many errors, change the visibility of the image to visible
  if (errors.length > 0) {
    for (let i = 0; i < errors.length; i++) {
      $('.hangman-drawing > img')[i].style.visibility = 'visible';
    }
  }
}
