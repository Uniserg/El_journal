g = true;
var s = '';

$('.zan').click(function(){
    id = $(this).attr('id');
    $('#cur_dz').css('display', 'block')
    $.ajax({
      type: "POST",
      url: "/get_dz",
      data: 'zan_id=' + id,
      success: function(msg) {
         $('#dz_data').text(msg);
      }});

    $('#change_dz').click(function(){
    $('#windowinput_dz').css('display', 'block')});


    $('#save').click(function(date_now){
    $.ajax({
            type: "POST",
            url: "/get_dz",
            data: 'input_dz=' + $('#input_dz').val() + '&zan_id=' + id,
            success: function(msg){
                $('#date_now').text(date_now);
                $('#dz_data').text($('#input_dz').val());
                $('#dz_data').text(msg);
            }

    })
    $('#windowinput_dz').css('display', 'none');
});


})
$('.stud').click(function() {
    id = $(this).attr('id');
    id_zan = $(this).attr('zan_id')
    $('#date').text($('#'+id).data('date'));
    var i = 0;
    while (id[i]!='d') {
        s += id[i];
        i += 1;
    }
    $('#fio').text($('#fio'+s).text());
    if (g == true){
        $('#windowinput').css('display', 'none')
    }
    else{
        $('#windowinput').css('display', 'block');
    }

});


$(document).mouseup(function (e) {
    var container = $("#windowinput");
    if (container.css('display') == 'block') g = true;
    else g = false;
    if (container.has(e.target).length === 0){
        container.hide();
        $('#select').val('');
        s = '';
    }
    var container = $("#windowinput_dz");
    if (container.css('display') == 'block') g = true;
    else g = false;
    if (container.has(e.target).length === 0){
        container.hide();
    }
    var container = $("#cur_dz");
    if (container.css('display') == 'block') g = true;
    else g = false;
    if (container.has(e.target).length === 0){
        container.hide();
    }
})

$('#button').click(function() {
    $.ajax({
          type: "POST",
          url: "/get_grade",
          data: "student=" + $('#' + id).data('student') +'&zan_id='+$('#'+id).data('zan_id') + '&summa='+ $('#summa'+s).text() + "&date=" + $('#' + id).data('date') + "&grade=" + $('#select').val() + '&comment=' + $('#comment').val(),
          success: function(msg) {
//              $('#'+id).html().replace($('#windowinput select').val(), "");
              $('#summa' + s).text(msg);
              $('#'+id).text($('#select').val());
//              $('#summa'+id_sum).text($('#grade'));
              $('#select').val('');
              $('#windowinput').css('display', 'none');
              s = ''
          }

    });
});