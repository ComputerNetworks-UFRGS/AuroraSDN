//var h = $(window).innerHeight() - (179 + 50 + 15); old
var ctrl_pressed = 0;
// resize Topology chart
function resizeTopologyChart(){
    //var h = $(window).innerHeight() - (241 + 50 + 15);
    var h = $(window).innerHeight() - (241 + 10);
    var w = d3.select('#data_plane').style('width').replace('px', '');
    outer.transition()
        .attr("width",w)
        .attr("height",h);
}

function initTopologyChart() {

    //var height = $(window).innerHeight() - (241 + 50 + 15);
    var height = $(window).innerHeight() - (241 + 10);
    var width = d3.select('#data_plane').style('width').replace('px', '');
    var fill = d3.scale.category20();

    var nodes = [
    //    {id: 0, reflexive: false},
    //    {id: 1, reflexive: true},
    //    {id: 2, reflexive: false}
    ],
            lastNodeId = -1,
            links = [
    //    {source: nodes[0], target: nodes[1], left: false, right: true},
    //    {source: nodes[1], target: nodes[2], left: false, right: true}
    ];

    function updateAllNodes(){
        //console.log(dataset);
        for (var i = 0; i < dataset['nodes'].length; i++) {
            var node_add = $.grep(nodes, function(e) {
                //console.log(dataset['nodes']);
                return e.id == dataset['nodes'][i]['id'];
            });
            //console.log(node_add);
            if (node_add.length === 0) {
                node = {id: dataset['nodes'][i]['id'], reflexive: false, type: dataset['nodes'][i]['type'], name: dataset['nodes'][i]['name']};
                nodes.push(node);
                //restart();
            } /*else {
                nodes[i].name = dataset['nodes'][i]['name'];
            }*/
        }
    }

    function updateAllLinks(){
        for (var i = 0; i < dataset['edges'].length; i++) {
            var src_node = {};
            var tar_node = {};
            for (var j = 0; j < nodes.length; j++) {
                if (nodes[j].id === dataset['edges'][i]['source']) {
                    src_node = nodes[j];
                } else {
                    if (nodes[j].id === dataset['edges'][i]['target']) {
                        tar_node = nodes[j];
                    }
                }
            }
            link = {source: src_node, target: tar_node};
            links.push(link);
            //restart();
        }
    }

    var topologyInterval = setInterval(updateTopologyChart, $( "#chart_update_selector" ).val()*1000);
    function updateTopologyChart(){
        console.log('***Topology Chart Sync***');
        redraw();
        clearInterval(topologyInterval);
        topologyInterval = setInterval(updateTopologyChart, $( "#chart_update_selector" ).val()*1000);
    }

    // mouse event vars
    var selected_node = null,
        selected_link = null,
        mousedown_link = null,
        mousedown_node = null,
        mouseup_node = null;

    // init svg
    outer = d3.select("#data_plane")
      .append("svg:svg")
        .attr("width", width)
        .attr("height", height)
        .attr("pointer-events", "all");

    var vis = outer
      .append('svg:g')
        .call(d3.behavior.zoom().on("zoom", rescale))
        .on("dblclick.zoom", null)
      .append('svg:g')
        .on("mousemove", mousemove)
        .on("mousedown", mousedown)
        .on("mouseup", mouseup);

    vis.append('svg:rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'lavender');

    // initialize all nodes and links
    updateAllNodes();
    updateAllLinks();

    // init force layout
    var force = d3.layout.force()
        .size([width, height])
        .nodes(nodes) // initialize with zero nodes
        .links(links)
        .linkDistance(100)
        .charge(-200)
        .on("tick", tick);


    // line displayed when dragging new nodes
    var drag_line = vis.append("line")
        .attr("class", "drag_line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", 0)
        .attr("y2", 0);
    // get layout properties
    var nodes = force.nodes(),
        //links = force.links(),
        node = vis.selectAll(".node"),
        link = vis.selectAll(".link");


    redraw();

    function mousedown() {
      //console.log('mousedown');
      $('svg').css('cursor','move');
    }

    function mousemove() {
      //console.log('mousemove');
    }

    function mouseup() {
      //console.log('mouseup');
      // clear mouse event vars
      $('svg').css('cursor','default');
      resetMouseVars();
    }

    function resetMouseVars() {
      mousedown_node = null;
      mouseup_node = null;
      mousedown_link = null;
    }

    function tick() {
      link.attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      node.attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
    }

    // rescale g
    function rescale() {
      if (ctrl_pressed)
           return;
      trans=d3.event.translate;
      scale=d3.event.scale;

      vis.attr("transform",
          "translate(" + trans + ")"
          + " scale(" + scale + ")");
    }

    // redraw force layout
    function redraw() {
        //console.log('redraw');
        //links.push({source: nodes[0], target: nodes[1]});
        var xScale = d3.scale.ordinal()
            .domain(d3.range(nodes.length))
            .rangeRoundBands([0, width], 0.05);

        updateAllNodes();
        updateAllLinks();

        link = vis.selectAll(".link");
        link = link.data(links);

        link.enter().insert("line", ".node")
            .attr("class", "link")
            .on("mousedown",
                function(d) {
                    mousedown_link = d;
                    if (mousedown_link == selected_link) selected_link = null;
                    else selected_link = mousedown_link;
                    selected_node = null;
                    redraw();
            })

        link.exit().remove();

        link.classed("link_selected", function(d) { return d === selected_link; });

        node = node.data(nodes);

        node.enter().insert("circle")
            .attr("class", "node")
            .attr("r", 5)
            .on('mousedown', function(d) {
                if (d3.event.ctrlKey)
                    return;
                // select node
                mousedown_node = d;
                //console.log(mousedown_node);
            })
            /*.transition()
                .duration(750)
                .ease("elastic")
                .attr("r", function(d) {
                if (d.type == 's'){
                    console.log(d.name);
                    console.log(applySizeToSwitch(d, calculateAggregateLoadValue(), calculateAggregateResourceValue()));
                    return applySizeToSwitch(d, calculateAggregateLoadValue(), calculateAggregateResourceValue());
                    //return 20;
                } else {
                    return 15;
                }
            })*/

        outer.selectAll('circle')
            .transition()
            .duration(750)
            .ease("elastic")
            .attr("r", function(d) {
            if (d.type == 's'){
                return applySizeToSwitch(d, getAggregateLoadValue()['overall_value'], getAggregateResourceValue());
                //return 20;s
            } else {
                return 5;
            }
        })

        // Calculates the switch data traffic rate based on received byes and flow duration
        function getSwitchRate(sw) {
            var header_obj = dataset['data_traffic']['header']['per_switch'][sw.name];
            var duration_seconds = 0;
            var received_bytes = 0;
            $.each(header_obj, function(index, value) {
                duration_seconds += parseInt(value['duration_seconds']);
                received_bytes += parseInt(value['received_bytes']);
            });
            if (duration_seconds !== 0 && received_bytes !== 0){
                var switch_traffic_rate = parseFloat(received_bytes/duration_seconds*8/1000).toFixed(2);
            } else {
                var switch_traffic_rate = 0;
            }
            return {'total':received_bytes, 'rate':switch_traffic_rate};
        }

        // Function to calculate the resource usage percentage to a switch
        function getSwitchResourceValue(sw) {
             var flows = dataset['data_traffic']['header']['per_switch'][sw.name];
             return flows.length;
        }

        // Function to calculate the control channel load percentage to a switch
        function getSwitchLoadValue(sw, crr_dataset) {
             var counters = crr_dataset['controller']['custom']['per_switch'][sw.name];
             var overall_value = 0;
             var in_value = 0;
             var out_value = 0;
             // For byte counters only
             $.each(counters, function(index, value) {
                if (index.indexOf('bytes') > -1) {
                    switch(index){
                        case 'port_status_bytes':
                            in_value += value;
                            break;
                        case 'send_packet_bytes':
                            out_value += value;
                            break;
                        case 'flow_removed_bytes':
                            in_value += value;
                            break;
                        case 'vendor_request_bytes':
                            out_value += value;
                            break;
                        case 'echo_reply_bytes':
                            in_value += value;
                            break;
                        case 'read_state_reply_bytes':
                            in_value += value;
                            break;
                        case 'features_reply_bytes':
                            in_value += value;
                            break;
                        case 'configuration_reply_bytes':
                            in_value += value;
                            break;
                        case 'barrier_reply_bytes':
                            in_value += value;
                            break;
                        case 'barrier_request_bytes':
                            out_value += value;
                            break;
                        case 'hello_request_bytes':
                            out_value += value;
                            break;
                        case 'echo_request_bytes':
                            out_value += value;
                            break;
                        case 'configuration_request_bytes':
                            out_value += value;
                            break;
                        case 'packet_in_bytes':
                            in_value += value;
                            break;
                        case 'hello_reply_bytes':
                            in_value += value;
                            break;
                        case 'modify_state_bytes':
                            out_value += value;
                            break;
                        case 'vendor_reply_bytes':
                            in_value += value;
                            break;
                        case 'features_request_bytes':
                            out_value += value;
                            break;
                        case 'read_state_request_bytes':
                            out_value += value;
                            break;
                        default:
                            console.log('Undefined Message');
                    }
                    overall_value += value;
                }
            });
            return {'overall_value':overall_value, 'in':in_value, 'out':out_value};
        }

        // Calculates the aggregate resource value
        function getAggregateResourceValue() {
            return dataset['controller']['custom']['aggregate']['flow_count'];
        }

        // Calculates the aggregate load value
        function getAggregateLoadValue() {
             //console.log('aggregate value');
             var counters = dataset['controller']['custom']['aggregate']['control_messages_count'];
             var overall_value = 0;
             var in_value = 0;
             var out_value = 0;
             // For byte counters only
             $.each(counters, function(index, value) {
                if (index.indexOf('bytes') > -1) {
                    switch(index){
                        case 'port_status_bytes':
                            in_value += value;
                            break;
                        case 'send_packet_bytes':
                            out_value += value;
                            break;
                        case 'flow_removed_bytes':
                            in_value += value;
                            break;
                        case 'vendor_request_bytes':
                            out_value += value;
                            break;
                        case 'echo_reply_bytes':
                            in_value += value;
                            break;
                        case 'read_state_reply_bytes':
                            in_value += value;
                            break;
                        case 'features_reply_bytes':
                            in_value += value;
                            break;
                        case 'configuration_reply_bytes':
                            in_value += value;
                            break;
                        case 'barrier_reply_bytes':
                            in_value += value;
                            break;
                        case 'barrier_request_bytes':
                            out_value += value;
                            break;
                        case 'hello_request_bytes':
                            out_value += value;
                            break;
                        case 'echo_request_bytes':
                            out_value += value;
                            break;
                        case 'configuration_request_bytes':
                            out_value += value;
                            break;
                        case 'packet_in_bytes':
                            in_value += value;
                            break;
                        case 'hello_reply_bytes':
                            in_value += value;
                            break;
                        case 'modify_state_bytes':
                            out_value += value;
                            break;
                        case 'vendor_reply_bytes':
                            in_value += value;
                            break;
                        case 'features_request_bytes':
                            out_value += value;
                            break;
                        case 'read_state_request_bytes':
                            out_value += value;
                            break;
                        default:
                            console.log('Undefined Message');
                    }
                    overall_value += value;
                }
            });
            return {'overall_value':overall_value, 'in':in_value, 'out':out_value};
        }

        // Function to apply Color to a switch
        function applyColorToSwitch(sw, loadValue, resourceValue) {
            var swLoadPercentage = getSwitchLoadValue(sw, dataset)['overall_value'] * 100 / loadValue;
            var swResourcePercentage = getSwitchResourceValue(sw) * 100 / resourceValue;
            var swColor = level['very_high']['color_value'];
            if (metrics['color'] === 'control_channel_load') {
                if (swLoadPercentage < level['low']['bottom']) {
                    swColor = level['very_low']['color_value'];
                } else {
                    if (swLoadPercentage < level['medium']['bottom']) {
                        swColor = level['low']['color_value'];
                    } else {
                        if (swLoadPercentage < level['high']['bottom']) {
                            swColor = level['medium']['color_value'];
                        } else {
                            if (swLoadPercentage < level['very_high']['bottom']) {
                                swColor = level['high']['color_value'];
                            }
                        }
                    }
                }
            } else {
                if (resourceValue === 0){
                    var swColor = level['very_low']['color_value'];
                } else {
                    if (swResourcePercentage < level['low']['bottom']) {
                        swColor = level['very_low']['color_value'];
                    } else {
                        if (swResourcePercentage < level['medium']['bottom']) {
                            swColor = level['low']['color_value'];
                        } else {
                            if (swResourcePercentage < level['high']['bottom']) {
                                swColor = level['medium']['color_value'];
                            } else {
                                if (swResourcePercentage < level['very_high']['bottom']) {
                                    swColor = level['high']['color_value'];
                                }
                            }
                        }
                    }
                }
            }
            return swColor;
        }

        // Function to apply Size to a switch
        function applySizeToSwitch(sw, loadValue, resourceValue) {
            var swLoadPercentage = getSwitchLoadValue(sw, dataset)['overall_value'] * 100 / loadValue;
            var swResourcePercentage = getSwitchResourceValue(sw) * 100 / resourceValue;
            var swSize = level['very_high']['size_value'];
            if (metrics['size'] === 'control_channel_load') {
                if (swLoadPercentage < level['low']['bottom']) {
                    swSize = level['very_low']['size_value'];
                } else {
                    if (swLoadPercentage < level['medium']['bottom']) {
                        swSize = level['low']['size_value'];
                    } else {
                        if (swLoadPercentage < level['high']['bottom']) {
                            swSize = level['medium']['size_value'];
                        } else {
                            if (swLoadPercentage < level['very_high']['bottom']) {
                                swSize = level['high']['size_value'];
                            }
                        }
                    }
                }
            } else {
                if (resourceValue === 0){
                    swSize = level['very_low']['size_value'];
                } else {
                    if (swResourcePercentage < level['low']['bottom']) {
                        swSize = level['very_low']['size_value'];
                    } else {
                        if (swResourcePercentage < level['medium']['bottom']) {
                            swSize = level['low']['size_value'];
                        } else {
                            if (swResourcePercentage < level['high']['bottom']) {
                                swSize = level['medium']['size_value'];
                            } else {
                                if (swResourcePercentage < level['very_high']['bottom']) {
                                    swSize = level['high']['size_value'];
                                }
                            }
                        }
                    }
                }
            }
            d3.select("#img_switch_resource_level").attr('width', swSize);
            d3.select("#img_switch_resource_level").attr('height', swSize);
            d3.select("#img_switch_load_level").attr('width', swSize);
            d3.select("#img_switch_load_level").attr('height', swSize);
            return swSize;
        }

        function getSwitchLoadLevel(sw) {
            var swColor = applyColorToSwitch(sw, getAggregateLoadValue()['overall_value'], getAggregateResourceValue());
            d3.select("#label_switch_load_level").style({'color':swColor});
            if (swColor == level['very_high']['color_value']) {
                d3.select("#img_switch_load_level").attr('src',level['very_high']['color_img']);
                return 'Very High';
            } else {
                if (swColor == level['high']['color_value']) {
                    d3.select("#img_switch_load_level").attr('src',level['high']['color_img']);
                    return 'High';
                } else {
                    if (swColor == level['medium']['color_value']) {
                        d3.select("#img_switch_load_level").attr('src',level['medium']['color_img']);
                        return 'Medium';
                    } else {
                        if (swColor == level['low']['color_value']) {
                            d3.select("#img_switch_load_level").attr('src',level['low']['color_img']);
                            return 'Low';
                        } else {
                            d3.select("#img_switch_load_level").attr('src',level['very_low']['color_img']);
                            return 'Very Low';
                        }
                    }
                }
            }
        }

        function getSwitchResourceLevel(sw) {
            var swSize = applySizeToSwitch(sw, getAggregateLoadValue()['overall_value'], getAggregateResourceValue());
            if (swSize == level['very_high']['size_value']) {
                return 'Very High';
            } else {
                if (swSize == level['high']['size_value']) {
                    return 'High';
                } else {
                    if (swSize == level['medium']['size_value']) {
                        return 'Medium';
                    } else {
                        if (swSize == level['low']['size_value']) {
                            return 'Low';
                        } else {
                            return 'Very Low';
                        }
                    }
                }
            }
        }

        // Get IN Traffic Rate for a switch
        function getSwitchControlTrafficRateIN(d) {
            if (typeof old_dataset !== 'undefined'){
                var difference_time = (dataset['controller']['custom']['aggregate']['last_synchronization_time'] - old_dataset['controller']['custom']['aggregate']['last_synchronization_time'])
                var difference_in_traffic = (getSwitchLoadValue(d, dataset)['in'] - getSwitchLoadValue(d, old_dataset)['in'])
                return "Traffic rate (IN): " + (difference_in_traffic*8/1000/difference_time).toFixed(2) + " kbps";
            } else {
                return "Traffic rate (IN): ? kbps";
            }
        }

        // Get OUT Traffic Rate for a switch
        function getSwitchControlTrafficRateOUT(d) {
            if (typeof old_dataset !== 'undefined'){
                var difference_time = (dataset['controller']['custom']['aggregate']['last_synchronization_time'] - old_dataset['controller']['custom']['aggregate']['last_synchronization_time'])
                var difference_out_traffic = (getSwitchLoadValue(d, dataset)['out'] - getSwitchLoadValue(d, old_dataset)['out'])
                return "Traffic rate (OUT): " + (difference_out_traffic*8/1000/difference_time).toFixed(2) + " kbps";
            } else {
                return "Traffic rate (OUT): ? kbps";
            }
        }

        function addNodeInformation(d) {
            //Get this bar's x/y values, then augment for the tooltip
            var xPosition = parseFloat(d.x) + xScale.rangeBand() / 2;
            var yPosition = parseFloat(d.y) / 2 + height / 2;
            if (d.type == "h"){
                //Setting tooltip title
                var tooltip_title = 'Host Information';
                //-----------------------------
                //Disabling all switch elements
                d3.select("#panel_switch_information").style({'display':'none'});
                d3.select("#panel_switch_load_level").style({'display':'none'});
                d3.select("#panel_switch_resource_level").style({'display':'none'});
                //-----------------------------
                //Enabling all host elements
                var label_host_ip_address = "IP address: " + d.name;
                var label_host_mac_address = "MAC address: " + d.id;

                d3.select("#label_host_ip_address ").text(label_host_ip_address );
                d3.select("#label_host_mac_address ").text(label_host_mac_address );

                d3.select("#panel_host_information").style({'display':'block'});
                //-----------------------------
            } else {
                //Setting tooltip title
                var tooltip_title = 'Switch Information';
                //-----------------------------
                //Disabling all host elements
                d3.select("#panel_host_information").style({'display':'none'});
                //-----------------------------
                //Enabling all switch elements
                var label_switch_dpid = "DPID: " + d.name;
                var label_control_traffic_rate_in = getSwitchControlTrafficRateIN(d);
                var label_control_traffic_rate_out = getSwitchControlTrafficRateOUT(d);
                var label_switch_load_percentage = "Channel Load Percentage " + (getSwitchLoadValue(d, dataset)['overall_value'] * 100 / getAggregateLoadValue()['overall_value']).toFixed(2) + " %";
                var label_switch_load_level = "Switch Level: " + getSwitchLoadLevel(d);
                var label_data_traffic_rate = "Average data traffic rate (per rule): " + getSwitchRate(d)['rate'] + " kbps";
                var label_data_traffic_total = "Data traffic (total): " + getSwitchRate(d)['total'] + " bytes";
                var label_rules = "Rules (installed/overall): " + getSwitchResourceValue(d) + "/" + getAggregateResourceValue();
                var label_switch_resource_percentage = "Resource Usage Percentage " + (getSwitchResourceValue(d) * 100 / getAggregateResourceValue()).toFixed(2) + " %";
                var label_switch_resource_level = "Switch Level: " + getSwitchResourceLevel(d);


                d3.select("#label_switch_dpid").text(label_switch_dpid);
                d3.select("#label_control_traffic_rate_in").text(label_control_traffic_rate_in);
                d3.select("#label_control_traffic_rate_out").text(label_control_traffic_rate_out);
                d3.select("#label_switch_load_percentage").text(label_switch_load_percentage);
                d3.select("#label_switch_load_level").text(label_switch_load_level);
                d3.select("#label_data_traffic_rate").text(label_data_traffic_rate);
                d3.select("#label_data_traffic_total").text(label_data_traffic_total);
                d3.select("#label_rules").text(label_rules);
                d3.select("#label_switch_resource_percentage").text(label_switch_resource_percentage);
                d3.select("#label_switch_resource_level").text(label_switch_resource_level);

                d3.select("#panel_switch_information").style({'display':'block'});
                d3.select("#panel_switch_load_level").style({'display':'block'});
                d3.select("#panel_switch_resource_level").style({'display':'block'});
                //-----------------------------
            }
            //Update the tooltip position and value
            d3.select("#tooltip_title").text(tooltip_title);


        }

        outer.selectAll('circle')
            .style("fill", function(d) {
                if (d.type === 'h') {
                    return '#000000';
                } else {
                    return applyColorToSwitch(d, getAggregateLoadValue()['overall_value'], getAggregateResourceValue());
                    //return '#0066cc';
                }
            }).classed('reflexive', function(d) {
            return d.reflexive;
        })
        .on("mouseover", function(d) {
            addNodeInformation(d);
            //Show the tooltip
            $("#node_information_panel").show();
        })
        .on("mouseout", function() {
            //Hide the tooltip
            $("#node_information_panel").hide();
        });

        node.exit().transition()
            .attr("r", 0)
            .remove();

        node.classed("node_selected", function(d) { return d === selected_node; });

        if (d3.event) {
            // prevent browser's default behavior
            d3.event.preventDefault();
        }

        force.start();
    }

    function spliceLinksForNode(node) {
      toSplice = links.filter(
        function(l) {
          return (l.source === node) || (l.target === node); });
      toSplice.map(
        function(l) {
          links.splice(links.indexOf(l), 1); });
    }

    function keyup() {
        // ctrl
        if (d3.event.keyCode === 17) {
            // unset ctrl pressed
            ctrl_pressed = 0;
            outer.selectAll('circle')
                .on('mousedown.drag', null)
                .on('touchstart.drag', null);
            outer.classed('ctrl', false);
        }
    }

    function keydown() {
      //if (!selected_node && !selected_link) return;
      switch (d3.event.keyCode) {
        case 8: // backspace
        case 17: { // ctrl
            outer.selectAll('circle').call(force.drag);
            outer.classed('ctrl', true);
            // set ctrl pressed
            ctrl_pressed = 1;
            break;
        }
        case 46: { // delete not used yet
          if (selected_node) {
            nodes.splice(nodes.indexOf(selected_node), 1);
            spliceLinksForNode(selected_node);
          }
          else if (selected_link) {
            links.splice(links.indexOf(selected_link), 1);
          }
          selected_link = null;
          selected_node = null;
          redraw();
          break;
        }
      }
    }

    // add keyboard callback
    d3.select(window)
        .on("keydown", keydown)
        .on('keyup', keyup);
}

