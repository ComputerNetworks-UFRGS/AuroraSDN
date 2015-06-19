function initRuleChart() {

    var margin = {top: 20, right: 80, bottom: 30, left: 50},
    //width = 500 - margin.left - margin.right,
    height = 210 - margin.top - margin.bottom;

    width = ($('#data_plane').width() / 2) - margin.left - margin.right;
    //console.log($( "#rule_chart" ).width());

    var parseDate = d3.time.format("%H:%M:%S %p").parse;

    var x = d3.time.scale()
            .range([0, width]);

    var y = d3.scale.linear()
            .range([height, 0]);

    var color = d3.scale.category10();

    var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

    var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

    var line = d3.svg.line()
            .interpolate("basis")
            .x(function(d) {
                return x(d.date);
            })
            .y(function(d) {
                return y(d.rules);
            });


    var svg = d3.select("#rule_chart").append("svg")
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
        .text("Rules vs Time");


    var data = [];
    data[0] = {'date': getTimeNow(), 'Total': '0', 'Idle': '0'}

    color.domain(d3.keys(data[0]).filter(function(key) {
        return key !== "date";
    }));

    //console.log(data.length);

    data.forEach(function(d) {
        d.date = parseDate(d.date);
    });

    var counters = color.domain().map(function(name) {
        return {
            name: name,
            values: data.map(function(d) {
                return {date: d.date, rules: +d[name]};
            })
        };
    });

    x.domain(d3.extent(data, function(d) {
        return d.date;
    }));

    y.domain([
        d3.min(counters, function(c) {
            return d3.min(c.values, function(v) {
                return v.rules;
            });
        }),
        d3.max(counters, function(c) {
            return d3.max(c.values, function(v) {
                return v.rules;
            });
        })
    ]);

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
            .text("Rules");

    var city = svg.selectAll(".city")
            .data(counters)
            .enter().append("g")
            .attr("class", "city");

    city.append("path")
            .attr("class", "line")
            .attr("d", function(d) {
                return line(d.values);
            })
            .style("stroke", function(d) {
                return color(d.name);
            });

    city.append("text")
            .datum(function(d) {
                return {name: d.name, value: d.values[d.values.length - 1]};
            })
            .attr("transform", function(d) {
                return "translate(" + x(d.value.date) + "," + y(d.value.rules) + ")";
            })
            .attr("x", 3)
            .attr("dy", ".35em")
            .text(function(d) {
                return d.name;
            });

    var ruleInterval = setInterval(updateRuleChart, $( "#chart_update_selector" ).val()*1000);
    function updateRuleChart() {
        console.log('***Rule Chart Sync***');
        //console.log(data);
        if (data.length === 20) {
            data.shift();
        }

        newObj = {'date': parseDate(getTimeNow()),
                  'Total': dataset['controller']['custom']['aggregate']['flow_count'].toString(),
                  'Idle': dataset['controller']['custom']['aggregate']['idle_flow_count'].toString()}

        data.push(newObj);

        var counters = color.domain().map(function(name) {
            return {
                name: name,
                values: data.map(function(d) {
                    return {date: d.date, rules: +d[name]};
                })
            };
        });

        x.domain(d3.extent(data, function(d) {
            return d.date;
        }));

        y.domain([
            d3.min(counters, function(c) {
                return d3.min(c.values, function(v) {
                    return v.rules;
                });
            }),
            d3.max(counters, function(c) {
                return d3.max(c.values, function(v) {
                    return v.rules;
                });
            })
        ]);

        // Select the section we want to apply our changes to
        var svg = d3.select("#rule_chart").transition();

        // Make the changes
        // svg.select(".line")   // change the line
        //           .duration(750)
        //           .attr("d", valueline(data));
        svg.select(".x.axis") // change the x axis
                .duration(750)
                .call(xAxis);
        svg.select(".y.axis") // change the y axis
                .duration(750)
                .call(yAxis);

        d3.select("#rule_chart").selectAll(".line")
                .transition()
                .duration(750)
                .attr("d", function(d) {
                    if (d.name === 'Idle') {
                        return line(counters[1].values);
                    } else {
                        return line(counters[0].values);
                    }
                });

        d3.select("#rule_chart").selectAll('.city')
                .select('text')
            .datum(function(d) {
                return {name: d.name, value: d.values[d.values.length - 1]};
            })
            .attr("transform", function(d) {
            if (d.name === 'Idle'){
                return "translate(" + x(counters[1].values[counters[1].values.length-1].date) + "," + y(counters[1].values[counters[1].values.length-1].rules) + ")";
            } else {
                return "translate(" + x(counters[0].values[counters[0].values.length-1].date) + "," + y(counters[0].values[counters[0].values.length-1].rules) + ")";
            }});
        clearInterval(ruleInterval);
        ruleInterval = setInterval(updateRuleChart, $( "#chart_update_selector" ).val()*1000);
    }

};