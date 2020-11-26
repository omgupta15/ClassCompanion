var disableAllElements = function() {
    var elementIds = ["newNoteButton", "copyTextButton", "saveButton", "noteName", "content"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = true;
    }
}

var enableAllElements = function() {
    var elementIds = ["newNoteButton", "copyTextButton", "saveButton", "noteName", "content"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = false;
    }
}

var reloadNotes = function() {
    disableAllElements();

    var xhttp = new XMLHttpRequest();
    xhttp.onerror = function() {
        enableAllElements();
        return Swal.fire(
            "An Error Occurred",
            "An error occurred while refreshing the notes list. Please refresh the page.",
            "error"
        );
    };
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var data = JSON.parse(this.responseText);
                if (data.status == "not-found") {
                    setCookie("userKey", data.userKey);
                    data.files = [];
                }
                console.log(data);
                var tableBody = document.getElementById("tableBody");
                if (data.files.length == 0) {
                    tableBody.innerHTML = `<tr>
                        <td colspan="3">No notes created! Click the button below to start creating notes.</td>
                    </tr>`;
                }
                else {
                    tableBody.innerHTML = "";
                    for (let i = 0; i < data.files.length; i++) {
                        tableBody.innerHTML += `<tr onclick="viewFile(${data.files[i].fileId})">
                            <td>${data.files[i].index}</td>
                            <td>${data.files[i].name}</td>
                            <td onload="var date = new Date(${data.files[i].created}); this.innerHTML = date.toString();"></td>
                        </tr>`;
                    }
                }
                return enableAllElements();
            }
            else {
                enableAllElements();
                return Swal.fire(
                    "An Error Occurred",
                    "An error occurred while refreshing the notes list. Please refresh the page.",
                    "error"
                );
            }
        }
    };
    xhttp.open("GET", window.location.href + "/getFilesList", true);
    xhttp.send();
}

var setCookie = function(cookieName, cookieValue, expiryDays = 300) {
    var date = new Date();
    date.setTime(date.getTime() + (expiryDays * 24 * 60 * 60 * 1000));
    var expires = "expires="+date.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
}

reloadNotes();
