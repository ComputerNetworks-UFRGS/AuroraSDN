var dataset;
var old_dataset;

// Dictionaries to change topology chart
// Control channel load is the sum of all control messages
// and Resource usage is the amount of flows installed on switches
var metrics = {'color': 'control_channel_load',
               'size': 'resource_usage'};
var level = {'very_high': {'top':100, 'bottom':20, 'size_value':35, 'color_value':'#FF3300', 'info':'red', 'color_img':'/Aurora/static/sdn/img/very_high.png'},
             'high': {'top':20, 'bottom':15, 'size_value':30, 'color_value':'#FF9933', 'info':'orange', 'color_img':'/Aurora/static/sdn/img/high.png'},
             'medium': {'top':15 , 'bottom':10, 'size_value':25, 'color_value':'#FAD739', 'info':'yellow', 'color_img':'/Aurora/static/sdn/img/medium.png'},
             'low': {'top':10, 'bottom':5, 'size_value':20, 'color_value':'#3DBA3D', 'info':'green', 'color_img':'/Aurora/static/sdn/img/low.png'},
             'very_low': {'top':5, 'bottom':0, 'size_value':15, 'color_value':'#6699FF', 'info':'blue', 'color_img':'/Aurora/static/sdn/img/very_low.png'}};

$("#form_configurations").submit(function(e)
{
    var postData = $(this).serializeArray();
    var formURL = $(this).attr("action");
    $.ajax(
    {
        url : formURL,
        type: "POST",
        data : postData,
        success:function(data, textStatus, jqXHR)
        {
            $("#btn_cancel_configurations").trigger( "click" );
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            //if fails
        }
    });
    e.preventDefault(); //STOP default action
    //e.unbind(); //unbind. to stop multiple form submit.
});


d3.json(url, function(json) {
    dataset = json;
    initTopologyChart();
    initMemoryChart();
    initRuleChart();
    initUpTrafficChart();
    initUpPacketsChart();
    initDownTrafficChart();
    initDownPacketsChart();
});

$( window ).resize(function() {
    resizeTopologyChart();
});

$(document).ready(function() {
    //Initialize as hidden
    $("#chart_panel_header").hide();
    $('#chart_panel_content').hide();
    $("#node_information_panel").hide();
});

function getTimeNow(){
    now = new Date();
    nowFormatted = now.getHours().toString()
        + ':'
        + (now.getMinutes()<10?'0':'') + now.getMinutes().toString()
        + ':'
        + (now.getSeconds()<10?'0':'') + now.getSeconds().toString()
        + (now.getHours()>12?' PM': ' AM');
    return nowFormatted;
}

var syncInterval = setInterval(updateChart, $( "#polling_interval_selector" ).val()*1000);
function updateChart(){
    //console.log('sync everything is here ' + $( "#sync_selector" ).val()*1000);
    d3.xhr(sync_url, function(error, response) {
        console.log('***Sync***');
        //console.log(sync_url);
        //console.log(error);
        //console.log(response);
        if (error == null){
            d3.json(url, function(error, json) {
                console.log('***Update Dataset***');
                old_dataset = dataset;
                dataset = json;
                //console.log(dataset);
                //console.log(url);
                //console.log(error);
                if (error != null){
                    console.log(error);
                }
            });
        } else {
            console.log(error);
        }
    });
    clearInterval(syncInterval);
    syncInterval = setInterval(updateChart, $( "#polling_interval_selector" ).val()*1000);
}

/*
function goFullscreen(id) {
    // Get the element that we want to take into fullscreen mode
    var element = document.getElementById(id);

    // These function will not exist in the browsers that don't support fullscreen mode yet,
    // so we'll have to check to see if they're available before calling them.

    if (element.mozRequestFullScreen) {
        // This is how to go into fullscren mode in Firefox
        // Note the "moz" prefix, which is short for Mozilla.
        element.mozRequestFullScreen();
    } else if (element.webkitRequestFullScreen) {
        // This is how to go into fullscreen mode in Chrome and Safari
        // Both of those browsers are based on the Webkit project, hence the same prefix.
        element.webkitRequestFullScreen();
    }
    // Hooray, now we're in fullscreen mode!
}

function exitFullscreen() {
  if(document.exitFullscreen) {
    document.exitFullscreen();
  } else if(document.mozCancelFullScreen) {
    document.mozCancelFullScreen();
  } else if(document.webkitExitFullscreen) {
    document.webkitExitFullscreen();
  }
}

function toggleFullScreen() {
    if (!document.fullscreenElement &&    // alternative standard method
        !document.mozFullScreenElement && !document.webkitFullscreenElement) {  // current working methods
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
        } else if (document.documentElement.mozRequestFullScreen) {
            document.documentElement.mozRequestFullScreen();
        } else if (document.documentElement.webkitRequestFullscreen) {
            document.documentElement.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
        }
    } else {
        if (document.cancelFullScreen) {
            document.cancelFullScreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
            document.webkitCancelFullScreen();
        }
    }
}
*/
