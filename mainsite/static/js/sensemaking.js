/**
 * Displays the text associated with a search query
 * @param data
 */
function render_text(data, tableId) {

    $('#' + tableId).empty()
    $('#' + tableId).DataTable({
        data: data,
        columns: [
            {title: "User"},
            {title: "Tweet"}
        ]
    });
    $('#' + tableId).addClass('.initialized').dataTable()
}

$('select').on('change', function (e) {

    if (this.id == 'observation_time') {
        if (this.value == 0) {
            $('#prediction_time').prop('disabled', true);
            $('#select_virality_threshold').prop('disabled', true);
        } else {
            $('#prediction_time').prop('disabled', false);
            $('#select_virality_threshold').prop('disabled', false);
        }
    } else if (this.id == 'prediction_time') {
        $('#select_hashtag').children('option:not(:first)').remove();
        // var radioValue = $("input[name='optradio']:checked").val();
        var prediction_time = this.value;
        var observation_time = $('#observation_time').prop('value');
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
        console.log($('#start-month').val() + "-" + $('#start-day').val())
        var data = {
            'observation_time': observation_time,
            'prediction_time': prediction_time,
            'start_month': startMonth,
            'start_day': startDay,
            'pred_type': 'ht'
        };
        $.ajax({
            type: 'GET', url: '/filterhashtags/', data: data, dataType: 'json',
            success: function (data) {
                for (var i in data.data.hashtags) {
                    var value = data.data.hashtags[i];
                    $('#select_hashtag').append($('<option>').text(value).attr('value', value));
                }
                $('#select_hashtag').prop('disabled', false);
            }
        });
    } else if (this.id == 'from-month') {
        populate_option(this.value, 'from-day');
    } else if (this.id == 'to-month') {
        populate_option(this.value, 'to-day');
    } else if (this.id == 'start-month') {
        console.log(this.value)
        populateOption(this.value, 'start-day', ['start-day'], []);

    }
});

$(".radio").change(function () {
    $('#observation_time').prop('disabled', false);
});

$("#show_advanced_search_btn").click(function () {
    transfer_search_text();
});

$("#search-category").change(function () {
    populate_plot_type(this.value);
});

$('#accordion').on('show.bs.collapse', function (e) {
    var searchFor = ""
    var usersOfHT = 0
    var grab = e.target.id == 'collapseOne' ? 'hashtag' : 'user';
    if ($('#hidden_search_text').prop('value') != '') {
        searchFor = $('#hidden_search_text').prop('value')
    }
    if (searchFor == '')  {
        var id = grab == 'hashtag'? 'hidden_hashtag_names': 'hidden_user_names';
        console.log(id)
        searchFor = $('#' + id).prop('value')
    } else {
        usersOfHT = grab == 'hashtag'? usersOfHT: 1;
    }

    var key = "" + grab + "_tweet"
    var tableId = grab == 'hashtag'? 'hashtag-tweet-table' : 'user-tweet-table'
    console.log('Grab from' + grab)
    console.log(tableId)
    var isInitialized = $('#' + tableId).hasClass('.initialized')
    console.log(isInitialized)
    console.log('Cleaning')
    if (!isInitialized) {

        $.ajax({
            type: 'GET',
            url: 'tweets',
            dataType: 'json',
            data: {'search_for': searchFor, 'grab': grab, 'users_of_ht': usersOfHT},
            success: function (data) {
                render_text(data.data, tableId);
            }
        })
    }

});

// $('.panel').on('hidden.bs.collapse', function (e) {
//     alert('Event fired on #' + e.currentTarget.id);
// })