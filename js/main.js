$(function() {

    // $('.collapse').collapse('hide');
    $('.list-group-item.active').parent().parent('.collapse').collapse('show');


    var pages = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('title'),
        // datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,

        prefetch: baseurl + '/search.json'
    });

    $('#search-box').typeahead({
        minLength: 0,
        highlight: true
    }, {
        name: 'pages',
        display: 'title',
        source: pages
    });

    $('#search-box').bind('typeahead:select', function(ev, suggestion) {
        window.location.href = suggestion.url;
    });


    // Markdown plain out to bootstrap style
    $('#markdown-content-container table').addClass('table');
    $('#markdown-content-container img').addClass('img-responsive');

    // Video modal
    $("#modal-video").on('shown.bs.modal', function(e){
        var videoId = $(e.relatedTarget).attr('data-video');
        var videoSrc = "https://player.vimeo.com/video/"+videoId+"?texttrack=en";
        $('#iframe-video').attr('src', videoSrc);
    });

    $('#modal-video').on('hidden.bs.modal', function (e) {
        $('#iframe-video').attr('src', '');
    });

});
