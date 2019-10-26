var csrftoken  = $('meta[name="csrf-token"]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

function addRef(id, iterator) {
    document.getElementById("add-" + iterator).style.display = "none";
    document.getElementById("remove-" + iterator).style.display = "block";
    $.post(id);
}

function removeRef(id, iterator) {
    document.getElementById("add-" + iterator).style.display = "block";
    document.getElementById("remove-" + iterator).style.display = "none";
    $.post(id);
}