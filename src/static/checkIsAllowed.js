$(document).ready(function () {
    $.post( window.location.href + 'checkAllowed', function (response) {
        for( x = 0; x < response.length; x++){
            if (response[x].success == "Not allowed") {
                $("#checkAllowed-" + response[x].id).remove();
            } else {
                $("#lock-" + response[x].id).remove();
            }
        }
        
    });

});


