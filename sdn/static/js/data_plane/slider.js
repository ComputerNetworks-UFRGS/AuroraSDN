$(function() {
    var select = $( "#polling_interval_selector" );
    var slider = $( "#polling_interval_slider" );
    slider.append("<div id='slider'></div>").slider({
        min: 1,
        max: 120,
        range: "min",
        value: select[ 0 ].selectedIndex + 1,
        slide: function( event, ui ) {
            //console.log('action slider onchange');
            select[ 0 ].selectedIndex = ui.value - 1;
        }
    });
    $( "#polling_interval_selector" ).change(function() {
        slider.slider( "value", this.selectedIndex + 1 );
    });
});

$(function() {
    var select = $( "#chart_update_selector" );
    var slider = $( "#chart_update_slider" );
    slider.append( "<div id='slider'></div>" ).slider({
        min: 1,
        max: 120,
        range: "min",
        value: select[ 0 ].selectedIndex + 1,
        slide: function( event, ui ) {
            //console.log('action slider onchange');
            select[ 0 ].selectedIndex = ui.value - 1;
        }
    });
    $( "#chart_update_interval_selector" ).change(function() {
        slider.slider( "value", this.selectedIndex + 1 );
    });
});

$(function() {
    var select = $( "#idle_timeout_selector" );
    var slider = $( "#idle_timeout_slider" );
    slider.append( "<div id='slider'></div>" ).slider({
        min: 1,
        max: 101,
        range: "min",
        value: select[ 0 ].selectedIndex + 1,
        slide: function( event, ui ) {
            //console.log('action slider onchange');
            select[ 0 ].selectedIndex = ui.value - 1;
        }
    });
    $( "#idle_timeout_selector" ).change(function() {
        slider.slider( "value", this.selectedIndex + 1 );
    });
});

$(function() {
    var select = $( "#hard_timeout_selector" );
    var slider = $( "#hard_timeout_slider" );
    slider.append( "<div id='slider'></div>" ).slider({
        min: 1,
        max: 31,
        range: "min",
        value: select[ 0 ].selectedIndex + 1,
        slide: function( event, ui ) {
            //console.log('action slider onchange');
            select[ 0 ].selectedIndex = ui.value - 1;
        }
    });
    $( "#hard_timeout_selector" ).change(function() {
        slider.slider( "value", this.selectedIndex + 1 );
    });
});