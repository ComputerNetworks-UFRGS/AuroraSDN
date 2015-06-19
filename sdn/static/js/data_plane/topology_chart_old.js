//var h = $(window).innerHeight() - (179 + 50 + 15); old
var h = $(window).innerHeight() - (241 + 50 + 15);
var w = d3.select('#data_plane').style('width').replace('px', '');
//console.log(h);
//console.log(w);

// set up SVG for D3
var width = w,
    height = h,
    colors = d3.scale.category10();

// init SVG element
var svg = d3.select('#data_plane')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr("pointer-events", "all");


// set up initial nodes and links
//  - nodes are known by 'id', not by index in array.
//  - reflexive edges are indicated on the node (as a bold black circle).
//  - links are always source < target; edge directions are set by 'left' and 'right'.
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

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds) {
            break;
        }
    }
}

function resizeTopologyChart(){
    var h = $(window).innerHeight() - (241 + 50 + 15);
    var w = d3.select('#data_plane').style('width').replace('px', '');
    svg.transition()
        .attr("width",w)
        .attr("height",h);
}

function initTopologyChart() {
    //console.log('**Initializing Topology**');
//    console.log('nodes');
//    console.log(nodes);
//    console.log('dataset[nodes]');
//    console.log(dataset['nodes']);
//
    for (var i = 0; i < dataset['nodes'].length; i++) {
        //console.log('1');
        node = {id: dataset['nodes'][i]['id'], reflexive: false, type: dataset['nodes'][i]['type'], name: dataset['nodes'][i]['name']};
        //node.x = 600;
        //node.y = 150;
        //console.log('2');
        nodes.push(node);
        restart();
    }
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
        restart();
    }
}

// init D3 force layout
var force = d3.layout.force()
        .nodes(nodes)
        .links(links)
        .size([width, height])
        .linkDistance(50)
        .charge(-200)
        .on('tick', tick)


// define arrow markers for graph links
// svg.append('svg:defs').append('svg:marker')
//        .attr('id', 'end-arrow')
//        .attr('viewBox', '0 -5 10 10')
//        .attr('refX', 6)
//        .attr('markerWidth', 3)
//        .attr('markerHeight', 3)
//        .attr('orient', 'auto')
//        .append('svg:path')
//        .attr('d', 'M0,-5L10,0L0,5')
//        .attr('fill', '#000');
//
// svg.append('svg:defs').append('svg:marker')
//        .attr('id', 'start-arrow')
//        .attr('viewBox', '0 -5 10 10')
//        .attr('refX', 4)
//        .attr('markerWidth', 3)
//        .attr('markerHeight', 3)
//        .attr('orient', 'auto')
//        .append('svg:path')
//        .attr('d', 'M10,-5L0,0L10,5')
//        .attr('fill', '#000');

// line displayed when dragging new nodes
var drag_line = svg.append('svg:path')
        .attr('class', 'link dragline hidden')
        .attr('d', 'M0,0L0,0');

// handles to link and node element groups
var path = svg.append('svg:g').selectAll('path'),
        circle = svg.append('svg:g').selectAll('g');

// mouse event vars
var selected_node = null,
        selected_link = null,
        mousedown_link = null,
        mousedown_node = null,
        mouseup_node = null;

function resetMouseVars() {
    mousedown_node = null;
    mouseup_node = null;
    mousedown_link = null;
}

// update force layout (called automatically each iteration)
function tick() {
    // draw directed edges with proper padding from node centers
    path.attr('d', function(d) {
        var deltaX = d.target.x - d.source.x,
                deltaY = d.target.y - d.source.y,
                dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
                normX = deltaX / dist,
                normY = deltaY / dist,
                //sourcePadding = d.left ? 17 : 12,
                sourcePadding = 1,
                //targetPadding = d.right ? 17 : 12,
                targetPadding = 1,
                sourceX = d.source.x + (sourcePadding * normX),
                sourceY = d.source.y + (sourcePadding * normY),
                targetX = d.target.x - (targetPadding * normX),
                targetY = d.target.y - (targetPadding * normY);
        return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
    });

    circle.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    });
}

// update graph (called when needed)
function restart() {
    var xScale = d3.scale.ordinal()
            .domain(d3.range(nodes.length))
            .rangeRoundBands([0, width], 0.05);

    // path (link) group
    path = path.data(links);

    // update existing links
    path.classed('selected', function(d) {
        return d === selected_link;
    })
            .style('marker-start', function(d) {
        return d.left ? 'url(#start-arrow)' : '';
    })
            .style('marker-end', function(d) {
        return d.right ? 'url(#end-arrow)' : '';
    });


    // add new links
    path.enter().append('svg:path')
            .attr('class', 'link')
            .classed('selected', function(d) {
        return d === selected_link;
    })
            .style('marker-start', function(d) {
        return d.left ? 'url(#start-arrow)' : '';
    })
            .style('marker-end', function(d) {
        return d.right ? 'url(#end-arrow)' : '';
    })
            .on('mousedown', function(d) {
        if (d3.event.ctrlKey)
            return;

        // select link
        mousedown_link = d;
        if (mousedown_link === selected_link)
            selected_link = null;
        else
            selected_link = mousedown_link;
        selected_node = null;
        restart();
    });

    // remove old links
    path.exit().remove();


    // circle (node) group
    // NB: the function arg is crucial here! nodes are known by id, not by index!
    circle = circle.data(nodes, function(d) {
        return d.id;
    });

    // update existing nodes (reflexive & selected visual states)
    circle.selectAll('circle')
            .style("fill", function(d) {
        if (d.type === 'h') {
            return '#000000';
        } else {
            return '#0066cc';
        }
    })
            .classed('reflexive', function(d) {
        return d.reflexive;
    })
            .on("mouseover", function(d) {
        console.log('tipo do nodo ' + d.type);
        //Get this bar's x/y values, then augment for the tooltip
        var xPosition = parseFloat(d.x) + xScale.rangeBand() / 2;
        var yPosition = parseFloat(d.y) / 2 + h / 2;
        var node_info = "";
        if (d.type == "h"){
            node_info = "Host IP: " + d.name;
        }else{
            node_info = "Switch DPID: " + d.name;
            var header_obj = dataset['data_traffic']['header']['per_switch'][d.name];
            //console.log(header_obj);
            var duration_seconds = 0;
            var received_bytes = 0;
            $.each(header_obj, function(index, value) {
                //console.log(parseInt(value['duration_seconds']));
                duration_seconds += parseInt(value['duration_seconds']);
                received_bytes += parseInt(value['received_bytes']);
            });
            if (duration_seconds !== 0 && received_bytes !== 0){
                var node_traffic_rate = "Data traffic rate: " + parseFloat(received_bytes/duration_seconds*8/1000).toFixed(2) + " kbps";
            } else {
                var node_traffic_rate = "Data traffic rate: " + 0 + " kbps";
            }
            //console.log(node_traffic_rate);

        }
        //Update the tooltip position and value
        d3.select("#node_id").text(node_info);
        d3.select("#node_traffic_rate").text(node_traffic_rate);
        //d3.select("#tooltip")
//                .style("left", xPosition + "px")
//                .style("top", yPosition + "px")
//                .select("#value")
          //      .text(info);
        //Show the tooltip
        $("#node_information_panel").show();
    })
            .on("mouseout", function() {
        //Hide the tooltip
        $("#node_information_panel").hide();
    });

    // add new nodes
    var g = circle.enter().append('svg:g');

    g.append('svg:circle')
            .attr('class', 'node')
            .attr('r', 12)
//            .style('fill', function(d) {
//        return (d === selected_node) ? d3.rgb(colors(d.id)).brighter().toString() : colors(d.id);
//    })
//            .style('stroke', function(d) {
//        return d3.rgb(colors(d.id)).darker().toString();
//    })
//            .classed('reflexive', function(d) {
//        return d.reflexive;
//    })
            .on('mouseover', function(d) {
        if (!mousedown_node || d === mousedown_node)
            return;
        // enlarge target node
        d3.select(this).attr('transform', 'scale(1.1)');
    })
            .on('mouseout', function(d) {
        if (!mousedown_node || d === mousedown_node)
            return;
        // unenlarge target node
        d3.select(this).attr('transform', '');
    })
            .on('mousedown', function(d) {
        if (d3.event.ctrlKey)
            return;

        // select node
        mousedown_node = d;
        if (mousedown_node === selected_node)
            selected_node = null;
        else
            selected_node = mousedown_node;
        selected_link = null;

        // reposition drag line
        drag_line
                .style('marker-end', 'url(#end-arrow)')
                .classed('hidden', false)
                .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y);

        restart();
    })
            .on('mouseup', function(d) {
        if (!mousedown_node)
            return;

        // needed by FF
        drag_line
                .classed('hidden', true)
                .style('marker-end', '');

        // check for drag-to-self
        mouseup_node = d;
        if (mouseup_node === mousedown_node) {
            resetMouseVars();
            return;
        }

        // unenlarge target node
        d3.select(this).attr('transform', '');

        // add link to graph (update if exists)
        // NB: links are strictly source < target; arrows separately specified by booleans
        var source, target, direction;
        if (mousedown_node.id < mouseup_node.id) {
            source = mousedown_node;
            target = mouseup_node;
            direction = 'right';
        } else {
            source = mouseup_node;
            target = mousedown_node;
            direction = 'left';
        }

        var link;
        link = links.filter(function(l) {
            return (l.source === source && l.target === target);
        })[0];

        if (link) {
            link[direction] = true;
        } else {
            link = {source: source, target: target, left: false, right: false};
            link[direction] = true;
            links.push(link);
        }

        // select new link
        selected_link = link;
        selected_node = null;
        restart();
    });

    // show node IDs
//    g.append('svg:text')
//            .attr('x', 0)
//            .attr('y', 4)
//            .attr('class', 'id')
//            .text(function(d) {
//        return d.id;
//    });

    // remove old nodes
    circle.exit().remove();

    // set the graph in motion
    force.start();
}

function updateTopology(){
//        myArray = [{'id': '73', 'foo': 'bar'}, {'id': '45', 'foo': 'bar'}];
//        var result = $.grep(myArray, function(e) {
//            return e.id == 45;
//        });
//        if (result.length == 0) {
//            console.log('nao achou');
//        } else {
//            console.log('achou');
//        }

        // For all nodes added
        for (var i = 0; i < dataset['nodes'].length; i++) {
            var node_add = $.grep(nodes, function(e) {
                return e.id == dataset['nodes'][i]['id'];
            });
            if (node_add.length === 0) {
                node = {id: dataset['nodes'][i]['id'], reflexive: false, type: dataset['nodes'][i]['type'], name: dataset['nodes'][i]['name']};
                nodes.push(node);
                restart();
            } else {
                nodes[i].name = dataset['nodes'][i]['name'];
            }
        }
        //console.log('ok');
        //restart();
        // For all nodes removed
//        for (var i = 0; i < nodes.length; i++) {
//            var node_remove = $.grep(dataset['nodes'], function(e) {
//                return e.id == nodes.id;
//            });
//            if (node_remove.length === 0) {
//                node = {id: dataset['nodes'][i]['id'], reflexive: false, type: dataset['nodes'][i]['type'], name: dataset['nodes'][i]['name']};
//                nodes.pop(node_remove);
//                restart();
//            }
//        }

        //console.log(dataset['edges']);
        //console.log(links);
        for (var i = 0; i < dataset['edges'].length; i++) {
            var link_add = $.grep(links, function(e) {
                return (e.source.id == dataset['edges'][i]['source'] && e.target.id == dataset['edges'][i]['target']);
            });
            if (link_add.length === 0) {
                var src_node_add = $.grep(nodes, function(e) {
                    return e.id == dataset['edges'][i]['source'];
                });
                var tar_node_add = $.grep(nodes, function(e) {
                    return e.id == dataset['edges'][i]['target'];
                });
                link = {source: src_node_add[0], target: tar_node_add[0]};
                links.push(link);
            }
        }

        restart();
        }

function mousedown() {
    // prevent I-bar on drag
    //d3.event.preventDefault();

    // because :active only works in WebKit?
    svg.classed('active', true);

    if (d3.event.ctrlKey || mousedown_node || mousedown_link)
        return;

    // insert new node at point
    var point = d3.mouse(this),
            node = {id: ++lastNodeId, reflexive: false};
    node.x = point[0];
    node.y = point[1];

//    nodes.push(node);
//    node = {id: ++lastNodeId, reflexive: false};
//    nodes.push(node);
    restart();
}

function mousemove() {
    if (!mousedown_node)
        return;

    // update drag line
    drag_line.attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + d3.mouse(this)[0] + ',' + d3.mouse(this)[1]);

    restart();
}

function mouseup() {
    if (mousedown_node) {
        // hide drag line
        drag_line
                .classed('hidden', true)
                .style('marker-end', '');
    }

    // because :active only works in WebKit?
    svg.classed('active', false);

    // clear mouse event vars
    resetMouseVars();
}

function spliceLinksForNode(node) {
    var toSplice = links.filter(function(l) {
        return (l.source === node || l.target === node);
    });
    toSplice.map(function(l) {
        links.splice(links.indexOf(l), 1);
    });
}

// only respond once per keydown
var lastKeyDown = -1;

function keydown() {
    d3.event.preventDefault();

    if (lastKeyDown !== -1)
        return;
    lastKeyDown = d3.event.keyCode;

    // ctrl
    if (d3.event.keyCode === 17) {
        circle.call(force.drag);
        svg.classed('ctrl', true);
    }

    if (!selected_node && !selected_link)
        return;
    switch (d3.event.keyCode) {
        case 8: // backspace
        case 46: // delete
            if (selected_node) {
                nodes.splice(nodes.indexOf(selected_node), 1);
                spliceLinksForNode(selected_node);
            } else if (selected_link) {
                links.splice(links.indexOf(selected_link), 1);
            }
            selected_link = null;
            selected_node = null;
            restart();
            break;
        case 66: // B
            if (selected_link) {
                // set link direction to both left and right
                selected_link.left = true;
                selected_link.right = true;
            }
            restart();
            break;
        case 76: // L
            if (selected_link) {
                // set link direction to left only
                selected_link.left = true;
                selected_link.right = false;
            }
            restart();
            break;
        case 82: // R
            if (selected_node) {
                // toggle node reflexivity
                selected_node.reflexive = !selected_node.reflexive;
            } else if (selected_link) {
                // set link direction to right only
                selected_link.left = false;
                selected_link.right = true;
            }
            restart();
            break;
    }
}

/*var topologyInterval = setInterval(updateTopologyChart, $( "#sync_selector" ).val()*1000);
function updateTopologyChart(){
    //console.log('sync everything is here ' + $( "#sync_selector" ).val()*1000);
    d3.xhr(sync_url, function(error, response) {
        console.log('***Topology Sync***');
        //console.log(sync_url);
        //console.log(error);
        //console.log(response);
        if (error != null){
            console.log(error);
        }
    });
    d3.json(url, function(error, json) {
        dataset = json;
        //console.log(dataset);
        //console.log(url);
        //console.log(error);
        if (error == null){
            updateTopology();
        }
    });
    clearInterval(topologyInterval);
    topologyInterval = setInterval(updateTopologyChart, $( "#sync_selector" ).val()*1000);
}*/

var topologyInterval = setInterval(updateTopologyChart, $( "#chart_update_selector" ).val()*1000);
function updateTopologyChart(){
    console.log('***Topology Chart Sync***');
    updateTopology();
    clearInterval(topologyInterval);
    topologyInterval = setInterval(updateTopologyChart, $( "#chart_update_selector" ).val()*1000);
}

function keyup() {
    lastKeyDown = -1;

    // ctrl
    if (d3.event.keyCode === 17) {
        circle
                .on('mousedown.drag', null)
                .on('touchstart.drag', null);
        svg.classed('ctrl', false);
    }
}

// app starts here
// COMMENT FOR DEVELOPMENT
/*svg.on('mousedown', mousedown)
        .on('mousemove', mousemove)
        .on('mouseup', mouseup);
d3.select(window)
        .on('keydown', keydown)
        .on('keyup', keyup);
restart();*/
