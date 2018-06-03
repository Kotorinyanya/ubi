function get_topic(appid, end_date, window_length) {
    let API = "/apps/" + appid + "/results";
    // Show placeholder & hide chart.
    $("#emotion-placeholder").show();
    $("#positive-tag-placeholder").show();
    $("#negative-tag-placeholder").show();
    $("#review-placeholder").show();
    $("#emotion-pie").hide();
    $("#positive-tag-pie").hide();
    $("#negative-tag-pie").hide();
    $("#phrase-placeholder").show();
    $("#up-phrase-centent").hide();
    $("#down-phrase-centent").hide();
    $("#up-reviews").hide();
    $("#down-reviews").hide();
    // Send AJAX.
    $.getJSON(
        API,
        {
            "window_length": window_length,
            "window_end_date": end_date
        },
        function (json) {
            let data = json["data"];
            // Show emotion.
            let emotion = [];
            for (let k in data["emotion"]) {
                emotion.push({
                    key: k,
                    y: data["emotion"][k]
                });
            }
            $("#emotion-placeholder").hide();
            $("#emotion-pie svg").html("");
            $("#emotion-pie").show();
            show_pie("#emotion-pie svg", "Emotion", emotion);
            // Show positive tags.
            let tags = [];
            for (let k in data["top_up_tags"]) {
                tags.push({
                    key: k,
                    y: data["top_up_tags"][k]
                });
            }
            $("#positive-tag-placeholder").hide();
            $("#positive-tag-pie svg").html("");
            $("#positive-tag-pie").show();
            show_pie("#positive-tag-pie svg", "Positive", tags);
            // Show negative tags.
            tags = [];
            for (let k in data["top_down_tags"]) {
                tags.push({
                    key: k,
                    y: data["top_down_tags"][k]
                });
            }
            $("#negative-tag-placeholder").hide();
            $("#negative-tag-pie svg").html("");
            $("#negative-tag-pie").show();
            show_pie("#negative-tag-pie svg", "Negative", tags);
            // Show phrases.
            $("#phrase-placeholder").hide();
            let phrase = "";
            for (let k in data["top_up_sentences"]) {
                let weight = data["top_up_sentences"][k];
                phrase += "<li class=\"alert alert-success\" role=\"alert\">\n" +
                    k +
                    "      </li>"
            }
            $("#up-phrase-centent").html(phrase).show();
            phrase = "";
            for (let k in data["top_down_sentences"]) {
                let weight = data["top_down_sentences"][k];
                phrase += "<li class=\"alert alert-danger\" role=\"alert\">\n" +
                    k +
                    "      </li>"
            }
            $("#down-phrase-centent").html(phrase).show();
            // Show reviews.
            $("#review-placeholder").hide();
            let reviews = "";
            for (let k in data["top_up_reviews"]) {
                let rev = data["top_up_reviews"][k]["content"];
                reviews += "<div class=\"card text-white bg-success\">\n" +
                    "  <div class=\"card-body\">\n" +
                    rev +
                    "  </div>\n" +
                    "</div>"
            }
            $("#up-reviews").html(reviews).show();
            reviews = "";
            for (let k in data["top_down_reviews"]) {
                let rev = data["top_down_reviews"][k]["content"];
                reviews += "<div class=\"card text-white bg-danger\">\n" +
                    "  <div class=\"card-body\">\n" +
                    rev +
                    "  </div>\n" +
                    "</div>"
            }
            $("#down-reviews").html(reviews).show();
        });
}

function show_pie(selector, title, content) {
    element = $(selector);
    let w = element.width();
    let h = w * 1.2;
    element.height(h);
    nv.addGraph(function () {
        let chart = nv.models.pieChart()
            .x(function (d) {
                return d.key
            })
            .y(function (d) {
                return d.y
            })
            .donut(true)
            .labelsOutside(true)
            .width(w)
            .height(h)
            .padAngle(.08)
            .cornerRadius(5);
        chart.title(title);
        d3.select(selector)
            .datum(content)
            .transition().duration(1200)
            .call(chart);
        return chart;
    });
}