/**
 * Global plot variables
 */

var d3 = Plotly.d3;

var gd3 = d3.select('#distribution_plot')
    .style({
        width: 100 + '%',
        height: 400,
    });

var gd = gd3.node();

var gd3_user = d3.select('#user_distribution_plot')
    .style({
        width: 100 + '%',
        height: 400,
    });

var gd_user = gd3_user.node();

var gd3_virality = d3.select('#actual_dist_plot_area')
    .style({
        width: 100 + '%',
        height: 400,
    });

var gd_virality = gd3_virality.node();

/**
 * Updates the plot type of a specific plot object
 * @param pltObj
 * @param pltType
 */
function updatePlotType(pltObj, pltType) {
    var dataUpdate;
    if (pltType == 'tonexty') dataUpdate = {type: 'scatter', fill: pltType};
    else if (pltType == 'scatter') dataUpdate = {type: pltType, fill: ''};
    else if (pltType == 'bar') dataUpdate = {type: pltType}
    else return -1
    Plotly.update(pltObj, dataUpdate)
}

/**
 * Plot functions
 */

function plot_hist(obj, data, re_layout) {
    console.log(data);
    var trace = {
        x: data,
        type: 'histogram',
    };
    var layout = {
        xaxis: {
            title: "Number of followers"
        },
        yaxis: {
            title: "Frequency"
        }
    }
    console.log(trace);
    if (re_layout) Plotly.newPlot(obj, [trace], layout);
    else Plotly.plot(obj, [trace], layout);
}

/**
 * Resets the table that displays the tweet texts associated with hashtags or users.
 */

function resetDataTable() {
    var userTableIsInitialized = $('#user-tweet-table').hasClass('.initialized')
    var hashtagTableIsInitialized = $('#hashtag-tweet-table').hasClass('.initialized')

    if (userTableIsInitialized) {
        var userTweetTable = $('#user-tweet-table').DataTable()

        $('#user-tweet-table').removeClass(".initialized")

        userTweetTable.destroy();

        $('#collapseTwo').collapse('hide')
        $('#collapseOne').collapse('hide')
    }
    //TODO: Hashtag table reset
    console.log("Hashtag table is initialized" + hashtagTableIsInitialized);
    if (hashtagTableIsInitialized) {
        var hashtagTweetTable = $('#hashtag-tweet-table').DataTable()
        $('#hashtag-tweet-table').removeClass(".initialized")
        hashtagTweetTable.destroy();
    }

}

function setupTweetText(elementId, values) {
    for (var i in values) {
        var disp = '<div class="card">\n' +
            '    <div class="card-header" role="tab" id="heading-"' + i + '>\n' +
            '      <h5 class="mb-0">\n' +
            '        <a data-toggle="collapse" href="#collapse-"' + i + ' aria-expanded="true" ' +
            '           aria-controls="collapseOne"> Tweets about \n' + values[i] +
            '        </a>\n' +
            '      </h5>\n' +
            '    </div>\n' +
            '\n' +
            '    <div id="collapse-"' + i + ' class="collapse" role="tabpanel" aria-labelledby="heading-"' + i +
            '         data-parent="#' + elementId + '">\n' +
            '      <div class="card-body" id="' + elementId + '-' + i + '-body">\n' +
            '      </div>\n' +
            '    </div>\n' +
            '  </div>'
        $('#' + elementId).prepend($(disp));
    }
}

/**
 * Changes the title of a element specified by its identifier
 * @param elementId the id
 * @param title the title
 * @param setAction action for plots
 */
function setTitle(elementId, title, setAction) {
    $("#" + elementId).empty();
    var titleWithAction = "<div>" + title +
        "<div class=\"pull-right\">\n" +
        "    <select id=\"plot-type-" + elementId + "\" class=\"form-control\">\n" +
        "        <option value=\"bar\" selected>Select Plot Type</option>\n" +
        "        <option value=\"bar\">Bar</option>\n" +
        "        <option value=\"tonexty\">Area</option>\n" +
        "        <option value=\"scatter\">Line</option>\n" +
        "    </select>\n" +
        "</div></div>";

    if (setAction) $('#' + elementId).prepend($(titleWithAction));
    else $("#" + elementId).append(title);
}



/**
 * Plots the distribution of one or multiple hashtags
 * @param stats
 * @param is_re_layout
 * @param plot_type
 */
function plot_hts_distribution(stats, is_re_layout, plot_type) {

    plot_type = (typeof plot_type !== 'undefined') ? plot_type : 'scatter';
    is_re_layout = (typeof is_re_layout !== 'undefined') ? is_re_layout : true;
    var data_trace = [];
    for (var i = 0; i < stats.length; i++) {
        var data_point = stats[i];
        if (data_point.length == 2) {
            data_trace.push({x: data_point[0], y: data_point[1], type: plot_type, fill: 'tonexty'});
        }
        else {
            data_trace.push({
                x: data_point[1],
                y: data_point[2],
                type: plot_type,
                fill: 'tonexty',
                name: data_point[0]
            });
        }
    }
    var layout = {
        xaxis: {
            title: 'Date',
        },
        yaxis: {
            title: 'Number of tweets',
        },
    }
    if (is_re_layout) {
        Plotly.newPlot(gd, data_trace, layout);
    }
    else {
        Plotly.plot(gd, data_trace, layout);
    }
}

/**
 * Creates a plotly plot from a data trace with a specified layout
 * @param data_trace Object: trace
 * @param layout Object: layout
 * @param re_layout boolean: a flag for updating or making a fresh plot
 */
function plot_from_trace(data_trace, layout, re_layout, canvas) {
    plt_canvas = (typeof canvas !== 'undefined') ? canvas : gd;
    if (re_layout) {
        Plotly.newPlot(plt_canvas, data_trace, layout);
    } else {
        Plotly.plot(plt_canvas, data_trace, layout);
    }
}

/**
 * plots the evolution in the distribution of top_k hashtags overtime
 * @param data
 */
function plot_top_k_evolution(data) {
    var lookup = {};

    function getData(date, ht) {
        var byDate, trace;
        if (!(byDate = lookup[date])) {
            byDate = lookup[date] = {};
        }

        if (!(trace = byDate[ht])) {
            trace = byDate[ht] = {
                x: [],
                y: [],
                id: [],
                text: [],
                marker: {size: []}
            };
        }
        return trace;
    }
    var names = []
    var name = '------------------------------------'
    for (var i = 0; i < data.length; i++) {
        var datum = data[i];
        var new_name = datum[0];
        if (new_name != name) {
            name = new_name;
            names.push(new_name);
        }

        var trace = getData(datum[1], datum[0]);
        trace.text.push(datum[0]);
        trace.id.push(datum[0]);
        trace.x.push(datum[4]);
        trace.y.push(datum[2]);
        trace.marker.size.push(datum[3] * 5000);
    }

    var days = Object.keys(lookup);

    var firstDay = lookup[days[0]];

    var hashtags = Object.keys(firstDay);

    var traces = [];
    for (i = 0; i < hashtags.length; i++) {
        var dt = firstDay[hashtags[i]];
        // One small note. We're creating a single trace here, to which
        // the frames will pass data for the different years. It's
        // subtle, but to avoid data reference problems, we'll slice
        // the arrays to ensure we never write any new data into our
        // lookup table:
        traces.push({
            name: hashtags[i],
            x: dt.x,
            y: dt.y,
            id: dt.id.slice(),
            text: dt.text.slice(),
            mode: 'markers',
            marker: {
                size: dt.marker.size.slice(),
                sizemode: 'area',
                sizeref: 200000
            }
        });
    }

    var frames = [];
    for (i = 0; i < days.length; i++) {
        frames.push({
            name: days[i],
            data: hashtags.map(function (ht) {
                return getData(days[i], ht);
            })
        })
    }

    var sliderSteps = [];
    for (i = 0; i < days.length; i++) {
        sliderSteps.push({
            method: 'animate',
            label: days[i],
            args: [[days[i]], {
                mode: 'immediate',
                transition: {duration: 300},
                frame: {duration: 300, redraw: false},
            }]
        });
    }

    var layout = {
        xaxis: {
            title: 'Number of users',
            range: [0, 5000]
        },
        yaxis: {
            title: 'Number of tweets',
            range: [0, 25000]
        },
        hovermode: 'closest',

        updatemenus: [{
            x: 0,
            y: 0,
            yanchor: 'top',
            xanchor: 'left',
            showactive: false,
            direction: 'left',
            type: 'buttons',
            pad: {t: 87, r: 10},
            buttons: [{
                method: 'animate',
                args: [null, {
                    mode: 'immediate',
                    fromcurrent: true,
                    transition: {duration: 600},
                    frame: {duration: 1000, redraw: false}
                }],
                label: 'Play'
            }, {
                method: 'animate',
                args: [[null], {
                    mode: 'immediate',
                    transition: {duration: 0},
                    frame: {duration: 0, redraw: false}
                }],
                label: 'Pause'
            }]
        }],
        // Finally, add the slider and use `pad` to position it
        // nicely next to the buttons.
        sliders: [{
            pad: {l: 130, t: 55},
            currentvalue: {
                visible: true,
                prefix: 'Days:',
                xanchor: 'right',
                font: {size: 20, color: 'green'}
            },
            steps: sliderSteps
        }]
    };


    Plotly.plot(gd, {
        data: traces,
        layout: layout,
        frames: frames,
    });
    return names
}

/**
 * Helper for displaying basic stats (scalar values)
 * @param basic_stats
 */
function showBaicStats(basic_stats) {
    $("#basic-stats").show();
    $("#tweet_count_lbl").empty();
    $("#user-count").empty();
    $("#tweet-coverage").empty();

    $("#tweet_count_lbl").append(basic_stats.tweet_count + " Tweet Counts!");
    $("#user-count").append(basic_stats.user_count + " User Counts!");
    $("#tweet-coverage").append(basic_stats.hashtag_coverage + " Hashtag Coverage!");
}


/**
 *
 * @param plt_data
 * @param plt_type
 * @returns {{data_trace: (Array|[null,null]), layout: {xaxis: {title: string}, yaxis: {title: string}}}|*}
 */
function prepare_multiple_trace(plt_data, plt_type) {
    x_pts = [];
    y_pts_1 = [];
    y_pts_2 = [];
    for (var i = 0; i < plt_data.length; i++) {
        var data_point = plt_data[i];
        x_pts.push(data_point[1]);
        y_pts_1.push(data_point[2]);
        y_pts_2.push(data_point[3]);
    }
    data_trace = [
        {x: x_pts, y: y_pts_1, type: plt_type, name: 'User distribution'},
        {x: x_pts, y: y_pts_2, type: plt_type, name: 'Tweet distribution'}
    ]
    var layout = {
        xaxis: {title: 'Date'},
        yaxis: {title: 'Trend'},
    }
    data = {'data_trace': data_trace, 'layout': layout};
    return data;
}

/**
 * Creates multiple traces for plotly visualization. Each trace is a single plot
 * @param plt_data The plot data from which a trace whould be generated. It is a multi-dimensional array.
 * axis = 0 correponds to a data point, and axis = 1 corresponds to an attribute (column)
 * @param name_idx int: the index for the column (axis=1) that is used as legend
 * @param x_idx int: the index for the x-axis (from the column)
 * @param y_idx int: the index for the y-axis
 * @param x_lab string: x label
 * @param y_lab string: y label
 * @param plt_type string: type of plot
 * @returns {{data_trace: Array, layout: {xaxis: {title: *}, yaxis: {title: *}}}|*}
 */
function prepare_multiple_trace_dynamic(plt_data, name_idx, x_idx, y_idx, x_lab, y_lab, plt_type) {
    var name = '-----------------------------'
    var x_pts = [];
    var y_pts = [];
    var data_trace = [];
    var names = []
    var autoCount = -1;
    if (x_idx == 'auto') autoCount = 0
    for (var i = 0; i < plt_data.length; i++) {
        var new_name = plt_data[i][name_idx];

        if (new_name != name) {

            if (y_pts.length > 0) {
                data_trace.push({
                    x: x_pts,
                    y: y_pts,
                    name: name,
                    type: plt_type,
                    fill: 'tonexty'
                });
                x_pts = [];
                y_pts = [];
            }
            name = new_name;
            names.push(new_name)
        }
        if (autoCount == -1) x_pts.push(plt_data[i][x_idx])
        else {
            x_pts.push(autoCount);
            autoCount += 10;
            console.log(autoCount)
        }
        y_pts.push(plt_data[i][y_idx])
    }
    data_trace.push({
        x: x_pts,
        y: y_pts,
        name: name,
        type: plt_type,
        fill: 'tonexty'
    });
    var layout = {
        xaxis: {title: x_lab},
        yaxis: {title: y_lab},
    }
    data = {'data_trace': data_trace, 'layout': layout, 'names': names};
    return data;
}

function prepare_for_hist(data) {
    x = []
    for (var i = 0; i < data.length; i++) x[i] = data[i];
    return x;
}

/**
 * Prepare a trace for plotly visualization. The trace corresponds to a single plot
 * @param plt_data
 * @param x_index
 * @param y_index
 * @param plt_type
 * @param x_lab
 * @param y_lab
 * @returns {{data_trace: [null], layout: {xaxis: {title: *}, yaxis: {title: *}}}|*}
 */
function prepare_single_trace(plt_data, x_index, y_index, plt_type, x_lab, y_lab) {
    x_pts = [];
    y_pts = [];

    for (var i = 0; i < plt_data.length; i++) {
        var data_point = plt_data[i];
        x_pts.push(data_point[x_index]);
        y_pts.push(data_point[y_index]);

    }
    var data_trace = {
        x: x_pts,
        y: y_pts,
        type: plt_type,
    };
    var layout = {
        xaxis: {
            title: x_lab,
        },
        yaxis: {
            title: y_lab,
        },
    }
    data = {'data_trace': [data_trace], 'layout': layout};
    return data;
}

/**
 * Handles advanced hashtag search
 *
 * @param plt_data
 * @param plot_type
 */
function handled_advanced_ht_search(plt_data, plot_type) {
    var res;
    if (plot_type == 0) {
        res = prepare_multiple_trace_dynamic(plt_data, 0, 1, 2, 'Date', 'Tweets trend', 'bar');
    } else if (plot_type == 1) {
        res = prepare_multiple_trace_dynamic(plt_data, 0, 1, 3, 'Date', 'Tweets trend', 'bar');
    } else if (plot_type == 2) {
        console.log(plt_data)
        res = prepare_multiple_trace_dynamic(plt_data, 0, 2, 3, 'Date', 'Tweets trend', 'bar');
    }

    plot_from_trace(res.data_trace, res.layout, true);
}

/**
 * Handles advanced user search
 *
 * @param plt_data
 * @param plot_type
 */
function handle_advanced_user_search(plt_data, plot_type) {
    var res;
    console.log(plt_data);
    if (plot_type == 0) {
        res = prepare_multiple_trace_dynamic(plt_data, 0, 3, 4, 'Date', 'Retweet trend', 'bar');
    } else if (plot_type == 1) {
        res = prepare_multiple_trace_dynamic(plt_data, 1, 2, 3, 'Date', 'Hashtag trend', 'bar');
    } else if (plot_type == 2) {
        res = prepare_multiple_trace_dynamic(plt_data, 0, 2, 3, 'Date', 'Tweets trend', 'bar');
    }

    plot_from_trace(res.data_trace, res.layout, true);
}

/**
 * Handles advanced keyword search
 * @param plt_data
 * @param plt_type
 */
function handle_advanced_keyword_search(plt_data, plt_type, keyword) {
    console.log(plt_data)
    user_data = plt_data.user_sum
    tweet_data = plt_data.tweet_sum
    setTitle("main-plot-title", "Tweets mentioning " + keyword, true);
    var res = prepare_single_trace(tweet_data, 0, 1, 'bar', 'Date', 'Number of tweets')
    plot_from_trace(res.data_trace, res.layout, true, gd)

    setTitle("user-plot-title", "Users mentioning " + keyword, true);
    res = prepare_single_trace(user_data, 0, 1, 'bar', 'Date', 'Number of users')
    plot_from_trace(res.data_trace, res.layout, true, gd_user)

}

/**
 * Listening to different interactive plot requests
 */


/**
 * Listener for the initial render
 */
if ('init_render' in data) {
    $("#basic-stats").hide();
    setTitle("main-plot-title", "Monthly popularity of top 10 hashtags for 2016", false);
    var names = plot_top_k_evolution(data.init_render[0]);
    var plt_data = data.init_render[1];
    setTitle("user-plot-title", "Retweet count of the top 10 active users", true);
    res = prepare_multiple_trace_dynamic(plt_data, 1, 2, 3, 'Date', 'Retweet Count', 'bar');
    var ht_names = ''
    var user_names = ''
    for (var i in names) ht_names = ht_names == ''? names[i] : ht_names + ',' + names[i];
    for (var i in res.names) user_names = user_names == ''? res.names[i] : user_names + ',' + res.names[i];

    $("#hidden_user_names").prop('value', res.names);
    $("#hidden_hashtag_names").prop('value', names);


    plot_from_trace(res.data_trace, res.layout, true, gd_user);
}


/**
 * Listener for point selection on a plot
 */

if (gd != null) {
    gd.on('plotly_click', function (data) {
        hideDiv("tweets-related-to-hashtags-card")
        var hashtag = data.points[0].text;
        $.ajax({
            type: 'GET',
            url: '/plot_search/',
            data: {
                'hashtag': hashtag
            },
            dataType: 'json',
            success: function (data) {
                console.log("Length of breadcrumb")
                if ($('#container-fluid ol li').length > 2) $('#bread-crumb li:last-child').remove();
                addBreadCrumb(hashtag)
                setAccordionTitle('hashtag-toggle-text', 'Tweets related to ' + hashtag);
                setAccordionTitle('user-toggle-text', 'Tweets related to the high-ranking users of ' + hashtag);
                setTitle("user-plot-title", "The rank of users involved in " + hashtag);
                plot_hist(gd_user, prepare_for_hist(data.rank), true)
                showBaicStats(data.basic_stats);
                setTitle("main-plot-title", "General tweets trend for " + hashtag, true);
                plot_hts_distribution(data.data.plot_selection, true, 'scatter');

            }
        });
    });
}

/**
 * Listener for the basic search. Handles the search through an ajax request
 */

$("#search_btn").click(function () {
    var search_text = $.trim($("#search_text").prop('value'));
    hideDiv("tweets-related-to-hashtags-card")
    resetDataTable();
    $('#accordion').collapse('hide')
    $("#hidden_search_text").prop('value', search_text)
    if (search_text == '') {
        var msg = "<p>Please specify a hashtag or a list of hashtags separated by comma!</p>"
        $("#modal-body").empty();
        $("#modal-title").empty();
        $("#modal-title").append("Info");
        $("#modal-body").append(msg);
        $("#message-modal").modal('show');
    } else {
        $.ajax({
            type: 'GET',
            url: 'search',
            data: {'search_text': search_text},
            dataType: 'json',
            success: function (data) {
                if ($('#container-fluid ol li').length > 2) $('#bread-crumb li:last-child').remove();
                addBreadCrumb(search_text)
                setAccordionTitle('hashtag-toggle-text', 'Tweets related to ' + search_text);
                setAccordionTitle('user-toggle-text', 'Tweets related to the high-ranking users of ' + search_text);
                showBaicStats(data.basic_stats)
                console.log(data.data)
                if (data.data.multiple == 1) hideDiv("user-distribution-plot-card")
                var plt_data = data.data.search;
                res = prepare_multiple_trace_dynamic(plt_data, 0, 1, 3, 'Date', 'Tweets trend', 'scatter');
                setTitle("main-plot-title", "General tweets trend for " + search_text, true);
                plot_from_trace(res.data_trace, res.layout, true);
                setTitle("tweet-text-title", "Tweets related to " + search_text, true);
                setTitle("user-plot-title", "The rank of users involved in " + search_text);
                plot_hist(gd_user, prepare_for_hist(data.data.rank), true)
            }
        })
    }
});

/**
 * Listener for the advanced search. Handles the search through an ajax request
 */

$("#advanced-search-button").click(function () {
    $('#observation_time').prop('value');
    $("#hidden_search_text").prop('value', search_text)
    hideDiv("tweets-related-to-hashtags-card")
    var from_year = $('#from-year').prop('value');
    var from_month = $('#from-month').prop('value');
    var from_day = $('#from-month').prop('value');

    var to_year = $('#to-year').prop('value');
    var to_month = $('#to-month').prop('value');
    var to_day = $('#to-month').prop('value');

    var category = $('#search-category').prop('value');

    var search_text = $('#advanced-search-text').prop('value');
    var plot_type = $('#plot-type').prop('value');
    $("#hidden_search_text").prop('value', search_text)

    resetDataTable();
    var data = {
        'from': from_year + '-' + format_month_day(from_month) + '-' + format_month_day(from_day),
        'to': to_year + '-' + format_month_day(to_month) + '-' + format_month_day(to_day),
        'category': category,
        'plot_type': plot_type,
        'advanced_search_text': search_text
    };

    $.ajax({
        type: 'GET',
        url: '/advancedsearch/',
        data: data,
        dataType: 'json',
        success: function (data) {
            if ($('#container-fluid ol li').length > 2) $('#bread-crumb li:last-child').remove();
            addBreadCrumb(search_text)
            setAccordionTitle('hashtag-toggle-text', 'Tweets related to ' + search_text);
            setAccordionTitle('user-toggle-text', 'Tweets related to the high-ranking users of ' + search_text);
            var plt_data = data.data;
            if (data.data.multiple == 1) hideDiv("user-distribution-plot-card")
            if (category == 'hashtag') handled_advanced_ht_search(plt_data, plot_type);
            else if (category == 'user') handle_advanced_user_search(plt_data, plot_type);
            else handle_advanced_keyword_search(plt_data, plot_type, search_text);

            if (category == 'hashtag') {
                plot_hist(gd_user, prepare_for_hist(data.rank), true)
            }
            $("#advanded_search_modal").modal('hide');
        }
    });
});

$('#predict_button').click(function () {
    // obs_time = int(request.POST.get('observation_time', None))
    //         prd_time = int(request.POST.get('prediction_time', None))
    //         threshold = int(request.POST.get('select_virality_threshold', None))
    //         target_ht = request.POST.get('select_hashtag', None)
    var obsTime = $('#observation_time').prop('value')
    var prdTime = $('#prediction_time').prop('value')
    var threshold = $('#select_virality_threshold').prop('value')
    var hashtag = $('#select_hashtag').prop('value');
    var startMonth = $('#start-month').prop('value');
    var startDay = $('#start-day').prop('value');
    if ($('#start-month').val() == '-1' && $('#start-month').val() == '-1') {
            startMonth = 1
            startDay = 1
        } else if ($('#start-month').val() == '-1') {
            startMonth = 1
            startDay = 1
        } else if ($('#start-day').val() == '-1') {
            startMonth = $('#start-month').val()
            startDay = 1
        } else {
            startMonth = $('#start-month').val()
            startDay = $('#start-day').val()
        }
    console.log('Under prediction')
    $.ajax({
        type: 'GET',
        url: '/predictcascades/',
        data: {
            'observation_time': obsTime,
            'prediction_time': prdTime,
            'select_virality_threshold': threshold,
            'select_hashtag': hashtag,
            'start_month': startMonth,
            'start_day': startDay,
            'predict': 1
        },
        dataType: 'json',
        success : function (data) {
            $('#virality-threshold-desc').empty()
            $('#current-cascade-size').empty()
            $('#predicted-label').empty()
            $('#confidence-indicator').empty()

            $('#virality-threshold-desc').append('Virality threshold at ' + threshold + "%")
            $('#current-cascade-size').append("Current size of " +  hashtag + " is " + data.data.current_size);
            $('#predicted-label').append("State: " + data.data.predicted_label);
            $('#confidence-indicator').append("Confidence: "  + data.data.confidence + "%");
            var range = data.data.predicted_label == 'Not-Viral'? 'low': 'high'
            $('#explanation-label span').text("A possible cause for " + hashtag + " hashtag to be " +
                data.data.predicted_label + " could be that the number of users involved in " +
                hashtag + " having sufficient active followers is " + range + " as shown in the above figure");

            var res = prepare_multiple_trace_dynamic(data.data.users_rank, 1, 1, 2, 'Users', 'Number of Followers', 'bar')
            plot_from_trace(res.data_trace, res.layout, true, gd_virality)
        }
    });

})
if ('users_rank' in data) {

}
$(document).on('change', '#plot-type-main-plot-title', function () {
    updatePlotType(gd, this.value);
});

$(document).on('change', '#plot-type-user-plot-title', function () {//do something})
    updatePlotType(gd_user, this.value);
});


$("checkbox").change(function () {
    if (this.checked) {
        alert("Explaining");
    } else {
        alert("Un Explaining");
    }
});
window.onresize = function () {
    Plotly.Plots.resize(gd);
};

