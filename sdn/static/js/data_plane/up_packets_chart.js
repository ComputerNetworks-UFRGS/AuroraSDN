function initUpPacketsChart(){
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

    var svg = d3.select("#up_packets_chart").append("svg")
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
        .text("Up Packets vs Time");


    var data = [];
    data[0] = {'date': getTimeNow(), 'Packet-In': '0', 'Read-State Reply': '0'}
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
            .text("Packets per second");

    var old_obj = {}
    var old_time = 0
    var upPacketsInterval = setInterval(updateUpPacketsChart, $( "#chart_update_selector" ).val()*1000);
    function updateUpPacketsChart() {
        console.log('***Up Packets Chart Sync***');
        packin = []
        reply = []
        data.forEach(function(entry){
           //console.log(entry);
           packin.push(entry['Packet-In']);
           reply.push(entry['Read-State Reply']);
        });

        packin = packin.map(function(item){
           return parseFloat(item);
        });

        reply = reply.map(function(item){
           return parseFloat(item);
        });

        //console.log(packin);
        //console.log(reply);


        graph_max = Math.max.apply(Math, packin) + Math.max.apply(Math, reply);;

        //console.log(data.length);
        //console.log(data);
        if (data.length === 20){
            data.shift();
        }

        var new_obj = {'date': parseDate(getTimeNow()),
                  'Packet-In': dataset['controller']['custom']['aggregate']['control_messages_count']['packet_in_count'].toString(),
                  'Read-State Reply': dataset['controller']['custom']['aggregate']['control_messages_count']['read_state_reply_count'].toString()}

        //TODO: calculo do valor máximo do eixo y
        if (new_obj['Packet-In'] + new_obj['Read-State Reply'] !== 0){
            graph_max = graph_max*1.5/100; // add 5% more in y axis
        }


        var new_time = dataset['controller']['custom']['aggregate']['last_synchronization_time'];

        //console.log('Read-State')
        //console.log(dataset['controller']['custom']['aggregate']['control_messages_count']['read_state_reply_bytes']);
        //console.log('Difference');
        //console.log(dataset['controller']['custom']['aggregate']['last_synchronization_time']);


        if (data.length === 1){
            // Add an object with zero values
            data.push({'date': parseDate(getTimeNow()), 'Packet-In': '0', 'Read-State Reply': '0'});
            old_obj = new_obj;
            old_time = dataset['controller']['custom']['aggregate']['last_synchronization_time'];
        }

        if (data.length > 1){
            // If last synchronization time is changed
            var difference_time = (new_time - old_time);
            //console.log('TIME ELAPSED');
            //console.log(difference_time);
            if (new_time !== old_time){
                var packet_in_rate = ((new_obj['Packet-In'] - old_obj['Packet-In']) / difference_time) * 100;
                var read_state_reply_rate = ((new_obj['Read-State Reply'] - old_obj['Read-State Reply']) / difference_time) * 100;
                //console.log('up packets packet_in');
                //console.log(packet_in_rate);
                //console.log('UP packets reply RATE');
                //console.log(read_state_reply_rate);
                var plot_obj = {'date': parseDate(getTimeNow()),
                                'Packet-In': packet_in_rate,
                                'Read-State Reply': read_state_reply_rate};

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

        var svg = d3.select("#up_packets_chart").transition();



        svg.selectAll("path")
            .transition()
                .duration(750)
            .attr("d", function(d) {
                //console.log(d);
                if (d.name === 'Packet-In'){
                    return area(browsers[0].values);
                } else {
                    return area(browsers[1].values);
                }
//                        console.log(browsers);
//                        return area(d.values);
            })
            .style("fill", function(d) {
                if (d.name === 'Packet-In'){
                    return area(browsers[0].name);
                } else {
                    return area(browsers[1].name);
                }
//                        return color(d.name);
            });

        d3.select("#up_packets_chart").selectAll('.browser').select("text")
            .datum(function(d) {
                return {name: d.name, value: d.values[d.values.length - 1]};
            })
            .attr("transform", function(d) {
            if (d.name === 'Packet-In'){
                return "translate(" + (x(browsers[0].values[browsers[0].values.length-1].date) + 10) + "," + y(browsers[0].values[browsers[0].values.length-1].y) + ")";
            } else {
                return "translate(" + (x(browsers[1].values[browsers[1].values.length-1].date) - 20) + "," + y(browsers[1].values[browsers[1].values.length-1].y) + ")";
             }});

        svg.select(".x.axis") // change the x axis
            .duration(750)
            .call(xAxis);
        svg.select(".y.axis") // change the y axis
            .duration(750)
            .call(yAxis);
        clearInterval(upPacketsInterval);
        upPacketsInterval = setInterval(updateUpPacketsChart, $( "#chart_update_selector" ).val()*1000);

    }
}