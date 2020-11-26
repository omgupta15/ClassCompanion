var newNoteButton = document.getElementById("newNoteButton");
var copyTextButton = document.getElementById("copyTextButton");
var saveButton = document.getElementById("saveButton");
var noteName = document.getElementById("noteName");
var content = document.getElementById("content");
var fileIdElement = document.getElementById("fileId");
var changesInfo = document.getElementById("changesInfo");

var savedText = '<i class="far fa-check-circle"></i>&nbsp; All Changes Saved';
var unsavedText = '<i class="far fa-exclamation-triangle"></i>&nbsp; Unsaved Changes';
var savingText = '<i class="fa fa-spinner fa-spin"></i>&nbsp; Saving Changes...';

var disableNoteEditor = function() {
    var elementIds = ["copyTextButton", "saveButton", "noteName", "content"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = true;
    }
}

var enableNoteEditor = function() {
    var elementIds = ["copyTextButton", "saveButton", "noteName", "content"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = false;
    }
}

var disableCreateButton = function() {
    var elementIds = ["newNoteButton"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = true;
    }
}

var enableCreateButton = function() {
    var elementIds = ["newNoteButton"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = false;
    }
}

var reloadNotes = function() {
    disableCreateButton();
    disableNoteEditor();

    var xhttp = new XMLHttpRequest();
    xhttp.onerror = function() {
        enableCreateButton();
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
                        var date = new Date(data.files[i].created);
                        date = date.toString();
                        tableBody.innerHTML += `<tr onclick="viewFile(${data.files[i].fileId})">
                            <td>${data.files[i].index}</td>
                            <td>${data.files[i].name}</td>
                            <td>${date}</td>
                        </tr>`;
                    }
                }
                return enableCreateButton();
            }
            else {
                enableCreateButton();
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

newNoteButton.addEventListener("click", function() {
    disableNoteEditor();
    disableCreateButton();

    var data = {
        fileId: null,
        name: "Untitled",
        text: ""
    };

    var xhttp = new XMLHttpRequest();
    xhttp.onerror = function() {
        enableCreateButton();
        return Swal.fire(
            "An Error Occurred",
            "An error occurred while creating a new note. Please try again!",
            "error"
        );
    };
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var data = JSON.parse(this.responseText);
                if (data.success) {
                    reloadNotes();
                    fileIdElement.innerHTML = data.fileId;
                    noteName.value = "Untitled";
                    content.value = "";
                    enableCreateButton();
                    enableNoteEditor();
                    onSavedChanges();
                }
                else {
                    enableCreateButton();
                    return Swal.fire(
                        "An Error Occurred",
                        "An error occurred while creating a new note. Please try again!",
                        "error"
                    );
                }
            }
            else {
                enableCreateButton();
                return Swal.fire(
                    "An Error Occurred",
                    "An error occurred while creating a new note. Please try again!",
                    "error"
                );
            }
        }
    };
    xhttp.open("POST", window.location.href + "/updateFile", true);
    xhttp.send(JSON.stringify(data));
});

var viewFile = function(fileId) {
    disableCreateButton();
    disableNoteEditor();

    var data = {fileId: fileId};

    var xhttp = new XMLHttpRequest();
    xhttp.onerror = function() {
        enableCreateButton();
        return Swal.fire(
            "An Error Occurred",
            "An error occurred while opening this note. Please try again!",
            "error"
        );
    };
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var data = JSON.parse(this.responseText);
                if (data.success) {
                    fileIdElement.innerHTML = data.fileId;
                    noteName.value = data.name;
                    content.value = data.content;
                    enableCreateButton();
                    enableNoteEditor();
                    onSavedChanges();
                }
                else {
                    enableCreateButton();
                    return Swal.fire(
                        "An Error Occurred",
                        "An error occurred while opening this note. Please try again!",
                        "error"
                    );
                }
            }
            else {
                enableCreateButton();
                return Swal.fire(
                    "An Error Occurred",
                    "An error occurred while opening this note. Please try again!",
                    "error"
                );
            }
        }
    };
    xhttp.open("POST", window.location.href + "/getFile", true);
    xhttp.send(JSON.stringify(data));
}

copyTextButton.addEventListener("click", function() {
    content.select();
    document.execCommand("copy");
});

var onSavingChanges = function() {
    changesInfo.innerHTML = savingText;
    disableCreateButton();
    disableNoteEditor();
};

var onSavedChanges = function() {
    changesInfo.innerHTML = savedText;
    saveButton.disabled = true;
};

var onUnsavedChanges = function() {
    changesInfo.innerHTML = unsavedText;
    saveButton.disabled = false;
};

noteName.addEventListener("keypress", onUnsavedChanges);
content.addEventListener("keypress", onUnsavedChanges);

saveButton.addEventListener("click", function() {
    onSavingChanges();

    var data = {
        fileId: fileIdElement.innerHTML,
        name: noteName.value,
        text: content.value
    };

    var xhttp = new XMLHttpRequest();
    xhttp.onerror = function() {
        enableNoteEditor();
        enableCreateButton();
        onUnsavedChanges();
        return Swal.fire(
            "An Error Occurred",
            "An error occurred while saving the note. Please try again!",
            "error"
        );
    };
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var data = JSON.parse(this.responseText);
                if (data.success) {
                    reloadNotes();
                    enableNoteEditor();
                    enableCreateButton();
                    onSavedChanges();
                    Swal.fire({
                        position: "top-end",
                        icon: "success",
                        title: "This note has been saved successfully.",
                        showConfirmButton: false,
                        timer: 1000
                    });
                }
                else {
                    enableNoteEditor();
                    enableCreateButton();
                    onUnsavedChanges();
                    return Swal.fire(
                        "An Error Occurred",
                        "An error occurred while creating a new note. Please try again!",
                        "error"
                    );
                }
            }
            else {
                enableNoteEditor();
                enableCreateButton();
                onUnsavedChanges();
                return Swal.fire(
                    "An Error Occurred",
                    "An error occurred while creating a new note. Please try again!",
                    "error"
                );
            }
        }
    };
    xhttp.open("POST", window.location.href + "/updateFile", true);
    xhttp.send(JSON.stringify(data));
});

var setCookie = function(cookieName, cookieValue, expiryDays = 300) {
    var date = new Date();
    date.setTime(date.getTime() + (expiryDays * 24 * 60 * 60 * 1000));
    var expires = "expires="+date.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
};



reloadNotes();
