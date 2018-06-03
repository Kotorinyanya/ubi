function get_trend(appid, start_date, end_date) {
    let API = "/apps/" + appid + "/changes";
    // Show placeholder & hide chart.
    $("#trend-placeholder").show();
    $("#trend-chart").hide();
    // Send AJAX.
    $.getJSON(
        API,
        {
            "start_date": start_date,
            "end_date": end_date
        },
        function (json) {
            let trend_data = to_trend_data(json["data"]);
            $("#trend-placeholder").hide();
            $("#trend-chart svg").html("");
            $("#trend-chart").show();
            show_trend(trend_data);
        });
}

function to_trend_data(raw_data) {
    let data = [];
    let types = {
        "new_up": [],
        "new_down": [],
        "up_to_down": [],
        "down_to_up": []
    };
    let maps = {
        "new_up": "New Positive Reviews",
        "new_down": "New Negative Reviews",
        "up_to_down": "Positive to Negative",
        "down_to_up": "Negative to Positive"
    };
    for (let i = 0; i < raw_data.length; ++i) {
        let timestamp = new Date(raw_data[i]["date"]).getTime();
        for (let k in raw_data[i]) {
            if (k !== "date") {
                types[k].push([timestamp, raw_data[i][k]])
            }
        }
    }
    for (let k in types) {
        data.push({
            "key": maps[k],
            "values": types[k]
        });
    }

    return data;
}

function show_trend(data) {
    nv.addGraph(function () {
        let chart = nv.models.stackedAreaChart()
            .x(function (d) {
                return d[0]
            })
            .y(function (d) {
                return d[1]
            })
            .clipEdge(true)
            .useInteractiveGuideline(true)
        ;
        chart.color(function (d, i) {
            colors = {
                "New Positive Reviews": "#2ECC71",
                "New Negative Reviews": "#E74C3C",
                "Positive to Negative": "#9B59B6",
                "Negative to Positive": "#F39C12"
            };
            return colors[d["key"]];
        });
        chart.controlOptions(["Stacked","Expanded"]);
        chart.controlLabels({"stacked":"Stacked","stream":"Stream","expanded":"Ratio"});
        chart.noData("There is no Data to display");

        chart.xAxis
            .showMaxMin(false)
            .tickFormat(function (d) {
                return d3.time.format('%x')(new Date(d))
            });

        chart.yAxis
            .tickFormat(d3.format(',.d'));

        d3.select('#trend-chart svg')
            .datum(data)
            .transition().duration(500).call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
}
