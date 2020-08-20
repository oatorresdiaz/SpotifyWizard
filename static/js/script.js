var results = [];

// 0: Off (no current animation)
// 1: On (running animation)
// 2: Powering off (when animation finishes stop)
var animateBool = false;

$(document).ready(function(){

    $("#classification_status").show();
    $(".main-table").hide();

    $("#classification_status").text("");

    //SPOTIFY_WIZARD_MERLIN_URL = "http://127.0.0.1:5001/";

    SPOTIFY_WIZARD_MERLIN_URL = "https://spotify-wizard-merlin.herokuapp.com/";

    $("#form").submit(function(e) {

        results = [];

        $("#classification_status").show();
        $(".main-table").hide();

        $("#classification_status").text("Looking up your liked songs...");

        e.preventDefault(); // Disable form submission

        var form = $(this);
        var url = form.attr('action');

        // Get all the user's saved tracks

        $.ajax({
            url: url,
            type: 'POST',
            data: form.serialize(),
            async: true,
            success: function (data) {

                if (data != null) {

                    classifyMusic(data, 5, returnResultsToSpotifyWizard);

                }
                else {

                    $("#classification_status").text("There was a problem accessing your liked songs. Please try again later.");

                }

            }

        });

    });

});


function classifyMusic(data, chunk_size, callback) {

    if (data["track_meta"].length < 1) {

        callback(data);

        return;

    }

    var numOfTracks = data["track_meta"].length;

    $("#classification_status").text("Classifying: " + data["track_meta"].length + " songs remaining...");

    // Call Merlin to filter out saved tracks

    var chunk = [];

    for (var i = 0; i < chunk_size; i++ ) {

        track_meta = data["track_meta"].shift();

        if (track_meta != null) {

            chunk.push(track_meta);

        }
        else {

            break;

        }

    }

    var dict = {"search_term": data["search_term"], "track_meta": chunk};

    $.ajax({
        url: SPOTIFY_WIZARD_MERLIN_URL + "classify-music",
        type: 'POST',
        data: JSON.stringify(dict),
        dataType: 'json',
        contentType: 'application/json',
        async: true,
        success: function (response) {

            var index;

            for (index in response) {

                results.push(response[index]);
            }

            classifyMusic(data, chunk_size, callback);

        }

    });

}

function returnResultsToSpotifyWizard(data) {

    let url = $("#form").attr('action');

    let dict = {"search_term": data["search_term"], "curated_playlist_ids": results};

    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(dict),
        dataType: 'json',
        contentType: 'application/json',
        async: true,
        success: function (response) {

            var trackNames = response["track_names"];

            for (var i = 0; i < trackNames.length; i++) {

                $('#curated-playlist-table > tbody:last-child').append('<tr><td>' + trackNames[i] + '</td></tr>');

            }

            $("#classification_status").hide();
            $(".main-table").show();

        }

    });

}