$(document).ready(function () {
    $('.checkAllows').each(function () {
        var idd = this.id.split("checkAllowed-")[1]
        $.post(this.id, function (response) {
            if (response.success == "Not allowed") {
                $("#checkAllowed-" + idd).remove();
            } else {
                $("#lock-" + idd).remove();
            }
        });
    });
});


