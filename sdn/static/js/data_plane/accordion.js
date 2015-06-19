var old_value = 0;

$(function() {
    $('#chart_panel_footer').click(function() {
        $('#chart_panel_content').toggle();
        if (old_value === 0){
            old_value = 1;
            $('#chart_panel_header').show();
            $('#chart_panel').css("margin-top", -351);
        } else {
            old_value = 0;
            $('#chart_panel_header').hide();
            $('#chart_panel').css("margin-top", -73);
        }
    });
});

//Old accordion
/*$(function() {
    $( "#accordion" ).accordion({
        collapsible: true
    });

    $('#accordion').click(function() {
        var active = $( "#accordion" ).accordion( "option", "active" );
        if (active !== old_value){
            if (active === false){
                $('#accordion').animate({
                    'marginTop' : "+=290px" //moves up
                });
            } else {
                $('#accordion').animate({
                    'marginTop' : "-=290px" //moves up
                });
            }
            old_value = active;
        }
    });
});
*/