/*
	*******************************************************************************
	This chart is not developed yet!

	This is a Donut chart presents the amount of packet-In message sub-types
	trafficked on the control channel that Floodlight v0.90 can retrieve by default
	*******************************************************************************
*/

/*
!function(){
	var Donut3D={};
	
	function pieTop(d, rx, ry, ir ){
		if(d.endAngle - d.startAngle == 0 ) return "M 0 0";
		var sx = rx*Math.cos(d.startAngle),
			sy = ry*Math.sin(d.startAngle),
			ex = rx*Math.cos(d.endAngle),
			ey = ry*Math.sin(d.endAngle);
			
		var ret =[];
		ret.push("M",sx,sy,"A",rx,ry,"0",(d.endAngle-d.startAngle > Math.PI? 1: 0),"1",ex,ey,"L",ir*ex,ir*ey);
		ret.push("A",ir*rx,ir*ry,"0",(d.endAngle-d.startAngle > Math.PI? 1: 0), "0",ir*sx,ir*sy,"z");
		return ret.join(" ");
	}

	function pieOuter(d, rx, ry, h ){
		var startAngle = (d.startAngle > Math.PI ? Math.PI : d.startAngle);
		var endAngle = (d.endAngle > Math.PI ? Math.PI : d.endAngle);
		
		var sx = rx*Math.cos(startAngle),
			sy = ry*Math.sin(startAngle),
			ex = rx*Math.cos(endAngle),
			ey = ry*Math.sin(endAngle);
			
			var ret =[];
			ret.push("M",sx,h+sy,"A",rx,ry,"0 0 1",ex,h+ey,"L",ex,ey,"A",rx,ry,"0 0 0",sx,sy,"z");
			return ret.join(" ");
	}

	function pieInner(d, rx, ry, h, ir ){
		var startAngle = (d.startAngle < Math.PI ? Math.PI : d.startAngle);
		var endAngle = (d.endAngle < Math.PI ? Math.PI : d.endAngle);
		
		var sx = ir*rx*Math.cos(startAngle),
			sy = ir*ry*Math.sin(startAngle),
			ex = ir*rx*Math.cos(endAngle),
			ey = ir*ry*Math.sin(endAngle);

			var ret =[];
			ret.push("M",sx, sy,"A",ir*rx,ir*ry,"0 0 1",ex,ey, "L",ex,h+ey,"A",ir*rx, ir*ry,"0 0 0",sx,h+sy,"z");
			return ret.join(" ");
	}

	function getPercent(d){
		return (d.endAngle-d.startAngle > 0.2 ?
				Math.round(1000*(d.endAngle-d.startAngle)/(Math.PI*2))/10+'%' : '');
	}	
	
	Donut3D.transition = function(id, data, rx, ry, h, ir){
		function arcTweenInner(a) {
		  var i = d3.interpolate(this._current, a);
		  this._current = i(0);
		  return function(t) { return pieInner(i(t), rx+0.5, ry+0.5, h, ir);  };
		}
		function arcTweenTop(a) {
		  var i = d3.interpolate(this._current, a);
		  this._current = i(0);
		  return function(t) { return pieTop(i(t), rx, ry, ir);  };
		}
		function arcTweenOuter(a) {
		  var i = d3.interpolate(this._current, a);
		  this._current = i(0);
		  return function(t) { return pieOuter(i(t), rx-.5, ry-.5, h);  };
		}
		function textTweenX(a) {
		  var i = d3.interpolate(this._current, a);
		  this._current = i(0);
		  return function(t) { return 0.6*rx*Math.cos(0.5*(i(t).startAngle+i(t).endAngle));  };
		}
		function textTweenY(a) {
		  var i = d3.interpolate(this._current, a);
		  this._current = i(0);
		  return function(t) { return 0.6*rx*Math.sin(0.5*(i(t).startAngle+i(t).endAngle));  };
		}
		
		var _data = d3.layout.pie().sort(null).value(function(d) {return d.value;})(data);
		
		d3.select("#"+id).selectAll(".innerSlice").data(_data)
			.transition().duration(750).attrTween("d", arcTweenInner);
			
		d3.select("#"+id).selectAll(".topSlice").data(_data)
			.transition().duration(750).attrTween("d", arcTweenTop);
			
		d3.select("#"+id).selectAll(".outerSlice").data(_data)
			.transition().duration(750).attrTween("d", arcTweenOuter); 	
			
		d3.select("#"+id).selectAll(".percent").data(_data).transition().duration(750)
			.attrTween("x",textTweenX).attrTween("y",textTweenY).text(getPercent); 	
	}
	
	Donut3D.draw=function(id, data, x */
/*center x*//*
, y*/
/*center y*//*
,
			rx*/
/*radius x*//*
, ry*/
/*radius y*//*
, h*/
/*height*//*
, ir*/
/*inner radius*//*
){
	
		var _data = d3.layout.pie().sort(null).value(function(d) {return d.value;})(data);
		
		var slices = d3.select("#"+id).append("g").attr("transform", "translate(" + x + "," + y + ")")
			.attr("class", "slices");
			
		slices.selectAll(".innerSlice").data(_data).enter().append("path").attr("class", "innerSlice")
			.style("fill", function(d) { return d3.hsl(d.data.color).darker(0.7); })
			.attr("d",function(d){ return pieInner(d, rx+0.5,ry+0.5, h, ir);})
			.each(function(d){this._current=d;});
		
		slices.selectAll(".topSlice").data(_data).enter().append("path").attr("class", "topSlice")
			.style("fill", function(d) { return d.data.color; })
			.style("stroke", function(d) { return d.data.color; })
			.attr("d",function(d){ return pieTop(d, rx, ry, ir);})
			.each(function(d){this._current=d;});
		
		slices.selectAll(".outerSlice").data(_data).enter().append("path").attr("class", "outerSlice")
			.style("fill", function(d) { return d3.hsl(d.data.color).darker(0.7); })
			.attr("d",function(d){ return pieOuter(d, rx-.5,ry-.5, h);})
			.each(function(d){this._current=d;});

		slices.selectAll(".percent").data(_data).enter().append("text").attr("class", "percent")
			.attr("x",function(d){ return 0.6*rx*Math.cos(0.5*(d.startAngle+d.endAngle));})
			.attr("y",function(d){ return 0.6*ry*Math.sin(0.5*(d.startAngle+d.endAngle));})
			.text(getPercent).each(function(d){this._current=d;});				
	}
	
	this.Donut3D = Donut3D;
}();

var salesData=[
	{label:"Packet-In", color:"#3366CC"},
	{label:"Packet-In_unicast", color:"#DC3912"},
	{label:"Packet-In_broadcast", color:"#FF9900"},
	{label:"Packet-In_L3_ARP", color:"#111111"},
	{label:"Packet-In_L3_IPv4", color:"#009900"},
	{label:"Packet-In_L3_LLDP", color:"#4444aa"},
	{label:"Packet-In_L4_ICMP", color:"#aa00aa"},
	{label:"Packet-In_L4_UDP", color:"#cccccc"}
];

var quotesData=[
	{label:"Packet-Out", color:"#3366CC"},
	{label:"Modify-State", color:"#DC3912"}
];

var svg = d3.select('body').append("svg").attr("width",700).attr("height",300);
//var svg = d3.select('#packet_counters').append("svg").attr("width",280).attr("height",180);

svg.append("g").attr("id","salesDonut");
svg.append("g").attr("id","quotesDonut");

Donut3D.draw("salesDonut", randomData(), 150, 150, 130, 100, 30, 0.4);
Donut3D.draw("quotesDonut", randomData2(), 450, 150, 130, 100, 30, 0);

function updateCounters(dataset){
    var data = [];
    data.push({'label':'Packet-In','color':'#3366CC','value':dataset['controller'][0]['packet_in']});
    data.push({'label':'Packet-In_unicast', 'color':'#DC3912','value':dataset['controller'][0]['packet_in_unicast']});
    data.push({'label':'Packet-In_broadcast', 'color':'#FF9900','value':dataset['controller'][0]['packet_in_broadcast']});
    data.push({'label':'Packet-In_L3_ARP', 'color':'#111111','value':dataset['controller'][0]['packet_in_L3_ARP']});
    data.push({'label':'Packet-In_L3_IPv4', 'color':'#009900','value':dataset['controller'][0]['packet_in_L3_IPv4']});
    data.push({'label':'Packet-In_L3_LLDP', 'color':'#4444aa','value':dataset['controller'][0]['packet_in_L3_LLDP']});
    data.push({'label':'Packet-In_L4_ICMP', 'color':'#aa00aa','value':dataset['controller'][0]['packet_in_L4_ICMP']});
    data.push({'label':'Packet-In_L4_UDP', 'color':'#cccccc','value':dataset['controller'][0]['packet_in_L4_UDP']});
    Donut3D.transition("salesDonut", data, 130, 100, 30, 0.4);
    var data2 = [];
    data2.push({'label':'Packet-Out','color':'#3366CC','value':dataset['controller'][0]['packet_out']});
    data2.push({'label':'Modify_State', 'color':'#DC3912','value':dataset['controller'][0]['modify_state']});
    Donut3D.transition("quotesDonut", data2, 130, 100, 30, 0);
}

var donut3DInterval = setInterval(updateDonut3DChart, $( "#sync_selector" ).val()*1000);
function updateDonut3DChart(){
    console.log("***Donut Chart Sync***")
    d3.json(url, function(error, json) {
        dataset = json;
        if (error == null){
            updateCounters(dataset);
        }
    });
    clearInterval(donut3DInterval);
    donut3DInterval = setInterval(updateDonut3DChart, $( "#sync_selector" ).val()*1000);
}
function randomData(){
	return salesData.map(function(d){
		return {label:d.label, value:1000*Math.random(), color:d.color};});
}

function randomData2(){
	return quotesData.map(function(d){
		return {label:d.label, value:1000*Math.random(), color:d.color};});
}*/
