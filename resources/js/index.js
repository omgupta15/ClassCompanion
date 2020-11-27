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
    windowResized();
}

var enableNoteEditor = function() {
    var elementIds = ["copyTextButton", "saveButton", "noteName", "content"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = false;
    }
    windowResized();
}

var disableCreateButton = function() {
    var elementIds = ["newNoteButton"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = true;
    }
    windowResized();
}

var enableCreateButton = function() {
    var elementIds = ["newNoteButton"];
    for (var i = 0; i < elementIds.length; i++) {
        document.getElementById(elementIds[i]).disabled = false;
    }
    windowResized();
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
                    tableBody.innerHTML = `<tr class="notes-row">
                        <td colspan="3">No notes created! Click the button below to start creating notes.</td>
                    </tr>`;
                }
                else {
                    tableBody.innerHTML = "";
                    document.getElementById("notesTable").style.display = "block";
                    for (let i = 0; i < data.files.length; i++) {
                        var date = new Date(data.files[i].created);
                        date = date.toString();
                        tableBody.innerHTML += `<tr class="notes-row" onclick="viewFile(${data.files[i].fileId});">
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
    windowResized();
});

var onSavingChanges = function() {
    changesInfo.innerHTML = savingText;
    disableCreateButton();
    disableNoteEditor();
    windowResized();
};

var onSavedChanges = function() {
    changesInfo.innerHTML = savedText;
    saveButton.disabled = true;
    windowResized();
};

var onUnsavedChanges = function() {
    changesInfo.innerHTML = unsavedText;
    saveButton.disabled = false;
    windowResized();
};

noteName.addEventListener("keypress", onUnsavedChanges);
noteName.addEventListener("keyup", onUnsavedChanges);
noteName.addEventListener("keydown", onUnsavedChanges);
content.addEventListener("keypress", onUnsavedChanges);
content.addEventListener("keyup", onUnsavedChanges);
content.addEventListener("keydown", onUnsavedChanges);

noteName.addEventListener("focus", windowResized);
content.addEventListener("focus", windowResized);

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
                        title: "Saved",
                        showConfirmButton: false,
                        timer: 750,
                        // animation: false
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

var urlBox = document.getElementById("urlBox");
var connectButton = document.getElementById("connectButton");
var meetingFrame = document.getElementById("meetingFrame");

urlBox.addEventListener("keypress", function(event) {
    if (event.key == "Enter" || event.keyCode == 13) {
        connectButton.click();
    }
});

function getIdFromYouTubeUrl(url){
    var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    var match = url.match(regExp);
    return (match&&match[7].length==11)? match[7] : false;
}

connectButton.addEventListener("click", function() {
    if (!urlBox.value) {
        return Swal.fire(
            "Enter a URL",
            "Please enter a valid URL to connect.",
            "error"
        );
    }
    try {
        var url = new URL(urlBox.value);
        if (url.host == "youtu.be" || url.host == "www.youtu.be" || url.host == "youtube.com" || url.host == "www.youtube.com") {
            var youtubeUrlId = getIdFromYouTubeUrl(urlBox.value);
            if (youtubeUrlId) {
                urlBox.value = `https://www.youtube.com/embed/${youtubeUrlId}?autoplay=1`;
            }
        }
    }
    catch (e) {
        return Swal.fire(
            "Invalid URL",
            "Please enter a valid URL to connect.",
            "error"
        );
    }
    console.log(urlBox.value);
    connectButton.disabled = true;
    meetingFrame.innerHTML = `<iframe src="${urlBox.value}" style="min-width: 100%; height: 69.3vh;"></iframe>`;
    Swal.fire({
        title: 'Starting the connection...',
        timer: 1000,
        showConfirmButton: false,
        willOpen: () => {
            Swal.showLoading();
        },
        willClose: () => {}
    }).then((result) => {});
});

var windowResized = function() {
    var height = window.innerHeight;
    var elementHeight = height - content.getBoundingClientRect().y - 25;
    content.style.height = elementHeight + "px";
};
window.onresize = windowResized;

$('[data-toggle="tooltip"]').tooltip();
reloadNotes();
windowResized();

window.onload = function() {
    var mobile = (/iphone|ipad|ipod|android|blackberry|mini|windows\sce|palm/i.test(navigator.userAgent.toLowerCase()));
    if (mobile) {
        Swal.fire(
            "Computer Recommended",
            "This website works best when used on a computer.",
            "info"
        );              
    }
};
