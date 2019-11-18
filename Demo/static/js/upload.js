function UploadLinkClick() {
    $("#upload-link").on("click", function() {
        $("#upload-modal").modal("show")
    })
}

function BrowseBtnClick() {
    $("#file-input").trigger("click")
}

function UploadPredictBtnClick() {
    var e = $("#input-url").val();
    if (e && 0 != e.trim().length) {
        var o = null;
        $("#file-input").val() && (o = $("#file-input")[0].files[0].name), o == e ? UploadPostedFile() : UploadFileFromURL(e)
    } else alert("Please browse and select an image")
}

function FileUploadOnChange() {
    $("#file-input").change(function(e) {
        $("#input-url").val(e.target.files[0].name)
    })
}

function UploadPostedFile() {
    BlockUI(!0), ProgressLoadingMsgs("Processing...");
    console.log("trying upload");
    var e = new FormData;
    e.append("type", "posted")
    e.append("file", $("#file-input")[0].files[0]),
    console.log(e.get("file")),
    $.ajax({
        url: "/get-classification", 
        type: "POST",
        data : e,
        processData: !1,
        contentType: !1
    }).done(function(e) {
        GetImagePrediction(PredictionType.UploadedImage, e),
        $("#upload-modal").modal("hide"), $("#input-url").val(""), $("#file-input").val("")
    }).fail(function(e, o, l) {
        console.log("upload failed"),
        $("#input-url").val(""), $("#file-input").val(""), UnBlockUI(), e.getAllResponseHeaders() && (alert("An error occurred while retrieving prediction for uploaded image,please check console for more details"), console.log("An occurred while retrieving prediction for uploaded image"), console.log("Error details:"), console.log(l))
    })
}
