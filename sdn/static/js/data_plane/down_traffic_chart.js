function initDownTrafficChart(){

    var margin = {top: 20, right: 80, bottom: 30, left: 50},
    //width = 500 - margin.left - margin.right,
    height = 210 - margin.top - margin.bottom;

    width = ($('#data_plane').width() / 2) - margin.left - margin.right;
    var parseDate = d3.time.format("%H:%M:%S %p").parse,
            formatPercent = d3.format(".0%");

    var x = d3.time.scale()
            .range([0, width]);

    var y = d3.scale.linear()
            .range([height, 0]);

    var color = d3.scale.category20();

    var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

    var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

    var area = d3.svg.area()
            .x(function(d) {
                return x(d.date);
            })
            .y0(function(d) {
                return y(d.y0);
            })
            .y1(function(d) {
                return y(d.y0 + d.y);
            });

    var stack = d3.layout.stack()
            .values(function(d) {
                return d.values;
            });

    var svg = d3.select("#down_traffic_chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .attr("font-size", 22)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 8 - (margin.top / 2))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        //.style("text-decoration", "underline")
        .text("Down Traffic vs Time");


    var data = [];
    data[0] = {'date': getTimeNow(), 'Send-Packet': '0', 'Modify-State': '0', 'Read-State Req': '0'}
    //console.log(data)
    color.domain(d3.keys(data[0]).filter(function(key) {
        return key !== "date";
    }));

    data.forEach(function(d) {
        d.date = parseDate(d.date);
    });

    var browsers = stack(color.domain().map(function(name) {
        return {
            name: name,
            values: data.map(function(d) {
                return {date: d.date, y: d[name] / 100};
            })
        };
    }));

    x.domain(d3.extent(data, function(d) {
        return d.date;
    }));
    //Defining max value for experiments
    y.domain([0, 0]);

    var browser = svg.selectAll(".browser")
            .data(browsers)
            .enter().append("g")
            .attr("class", "browser");

    browser.append("path")
            .attr("class", "area")
            .attr("d", function(d) {
                return area(d.values);
            })
            .style("fill", function(d) {
                return color(d.name);
            });

    browser.append("text")
            .datum(function(d) {
                return {name: d.name, value: d.values[d.values.length - 1]};
            })
            .attr("transform", function(d) {
                return "translate(" + x(d.value.date) + "," + y(d.value.y0 + d.value.y / 2) + ")";
            })
            .attr("x", -6)
            .attr("dy", ".35em")
            .text(function(d) {
                return d.name;
            });

    svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

    svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Control channel load (kbps)");

    var old_obj = {}
    var old_time = 0
    var downTrafficInterval = setInterval(updateDownTrafficChart, $( "#chart_update_selector" ).val()*1000);
    function updateDownTrafficChart() {
        console.log('***Down Traffic Chart Sync***');
        sendpack = []
        modstate = []
        req = []
        data.forEach(function(entry){
           //console.log(entry);
           sendpack.push(entry['Send-Packet']);
           modstate.push(entry['Modify-State']);
           req.push(entry['Read-State Req']);
        });

        sendpack = sendpack.map(function(item){
           return parseFloat(item);
        });

        modstate = modstate.map(function(item){
           return parseFloat(item);
        });

        req = req.map(function(item){
           return parseFloat(item);
        });

        //console.log(packin);
        //console.log(reply);

        graph_max = Math.max.apply(Math, sendpack) + Math.max.apply(Math, modstate) + Math.max.apply(Math, req);

        //console.log(data.length);
        //console.log(data);
        if (data.length === 20){
            data.shift();
        }

        var new_obj = {'date': parseDate(getTimeNow()),
                  'Send-Packet': dataset['controller']['custom']['aggregate']['control_messages_count']['send_packet_bytes'].toString(),
                  'Modify-State': dataset['controller']['custom']['aggregate']['control_messages_count']['modify_state_bytes'].toString(),
                  'Read-State Req': dataset['controller']['custom']['aggregate']['control_messages_count']['read_state_request_bytes'].toString()}

        //TODO: calculo do valor máximo do eixo y
        if (new_obj['Send-Packet'] + new_obj['Modify-State'] + new_obj['Read-State Req'] !== 0){
            graph_max = graph_max*1.5/100; // add 5% more in y axis
        }


        var new_time = dataset['controller']['custom']['aggregate']['last_synchronization_time'];

        //console.log('Read-State')
        //console.log(dataset['controller']['custom']['aggregate']['control_messages_count']['read_state_reply_bytes']);
        //console.log('Difference');
        //console.log(dataset['controller']['custom']['aggregate']['last_synchronization_time']);


        if (data.length === 1){
            // Add an object with zero values
            data.push({'date': parseDate(getTimeNow()), 'Send-Packet': '0', 'Modify-State': '0', 'Read-State Req': '0'});
            old_obj = new_obj;
            old_time = dataset['controller']['custom']['aggregate']['last_synchronization_time'];
        }

        if (data.length > 1){
            // If last synchronization time is changed
            var difference_time = (new_time - old_time);
            //console.log('TIME ELAPSED');
            //console.log(difference_time);
            if (new_time !== old_time){
                var send_packet_rate = ((new_obj['Send-Packet'] - old_obj['Send-Packet']) / difference_time * 8 / 1000) * 100;
                var modify_state_rate = ((new_obj['Modify-State'] - old_obj['Modify-State']) / difference_time * 8 / 1000) * 100;
                var read_state_req_rate = ((new_obj['Read-State Req'] - old_obj['Read-State Req']) / difference_time * 8 / 1000) * 100;
                //console.log('send-packet rate');
                //console.log(send_packet_rate);
                //console.log('modify-state rate');
                //console.log(modify_state_rate);
                //console.log('read state request rate');
                //console.log(read_state_req_rate);
                var plot_obj = {'date': parseDate(getTimeNow()),
                                'Send-Packet': send_packet_rate,
                                'Modify-State': modify_state_rate,
                                'Read-State Req': read_state_req_rate};

                // Adding object to plot
                data.push(plot_obj);

                // Update old object and old time instance
                old_obj = new_obj;
                old_time = new_time;
            }
        }

        var browsers = stack(color.domain().map(function(name) {
            return {
                name: name,
                values: data.map(function(d) {
                    return {date: d.date, y: d[name] / 100};
                })
            };
        }));

        x.domain(d3.extent(data, function(d) {
            return d.date;
        }));

        y.domain([0, graph_max]);

        var svg = d3.select("#down_traffic_chart").transition();


        svg.selectAll("path")
            .transition()
                .duration(750)
            .attr("d", function(d) {
                if (d.name === 'Send-Packet'){
                    return area(browsers[0].values);
                } else {
                    if (d.name === 'Modify-State'){
                        return area(browsers[1].values);
                    } else {
                        return area(browsers[2].values);
                    }
                }
//                        console.log(browsers);
//                        return area(d.values);
            })
            .style("fill", function(d) {
                if (d.name === 'Send-Packet'){
                    return area(browsers[0].name);
                } else {
                    if (d.name === 'Modify-State') {
                        return area(browsers[1].name);
                    } else {
                        return area(browsers[2].name);
                    }
                }
//                        return color(d.name);
            });

        d3.select("#down_traffic_chart").selectAll('.browser').select("text")
            .datum(function(d) {
                return {name: d.name, value: d.values[d.values.length - 1]};
            })
            .attr("transform", function(d) {
            if (d.name === 'Send-Packet'){
                return "translate(" + (x(browsers[0].values[browsers[0].values.length-1].date) + 10) + "," + y(browsers[0].values[browsers[0].values.length-1].y) + ")";
            } else {
                if (d.name === 'Modify-State') {
                    return "translate(" + (x(browsers[1].values[browsers[1].values.length-1].date) + 10) + "," + y(browsers[1].values[browsers[1].values.length-1].y) + ")";
                } else {
                    return "translate(" + (x(browsers[2].values[browsers[2].values.length-1].date) + 10) + "," + y(browsers[2].values[browsers[2].values.length-1].y) + ")";
                }
             }});

        svg.select(".x.axis") // change the x axis
            .duration(750)
            .call(xAxis);
        svg.select(".y.axis") // change the y axis
            .duration(750)
            .call(yAxis);
        clearInterval(downTrafficInterval);
        downTrafficInterval = setInterval(updateDownTrafficChart, $( "#chart_update_selector" ).val()*1000);

    }
}