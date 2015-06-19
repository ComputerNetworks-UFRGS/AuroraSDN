function selectController() {
    var new_action = "/Aurora/sdn/visualizations/data_plane/controller/" + $("#controller_selector" ).val() + "/view/";
    $('#form_select_controller').attr('action', new_action);
}