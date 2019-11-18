var showBbox = !1
  , PredictionType = {
    SampleImage: 1,
    UploadedImage: 2
};

function GetImagePrediction(e, o) {
    switch (BlockUI(!0),
    /*setTimeout(function() {
        ProgressLoadingMsgs("Checking image dimensions...")
    }, 100),
    setTimeout(function() {
        ProgressLoadingMsgs("Resizing image...")
    }, 1e3),
    setTimeout(function() {
        ProgressLoadingMsgs("Sending image to API for prediction...")
    }, 1e3), */
    e) {
    case PredictionType.SampleImage:
        GetSampleImagePrediction(o);
        break;
    case PredictionType.UploadedImage:
        GetImagePredictionUploadedFile(o)
    }
}

// same as posted image func for now
function GetSampleImagePrediction(o) {
    BlockUI(!0), ProgressLoadingMsgs("Processing...");
    console.log("trying upload");
    var e = new FormData;
    e.append("type", 'sample'),
    e.append("file", o),
    $.ajax({
        url: "/get-classification", 
        type: "POST",
        data : e,
        processData: !1,
        contentType: !1
    }).done(function(e) {
        GetImagePredictionUploadedFile(e),
        $("#upload-modal").modal("hide"), $("#input-url").val(""), $("#file-input").val("")
    }).fail(function(e, o, l) {
        console.log("upload failed"),
        $("#input-url").val(""), $("#file-input").val(""), UnBlockUI(), e.getAllResponseHeaders() && (alert("An error occurred while retrieving prediction for uploaded image,please check console for more details"), console.log("An occurred while retrieving prediction for uploaded image"), console.log("Error details:"), console.log(l))
    })
}


function GetImagePredictionUploadedFile(e) {
    console.log("GetImagePredictionUploadedFile"),  
    console.log(e),
    PopulateModal(e)
    $("#upload-modal").modal("hide")
}

function PopulateModal(e, o) {
    console.log("PopulateModal"),
    $(".modal img").attr("src", e),
    ShowPredictionModal()
}

function ShowPredictionModal() {
    console.log("ShowPredictionModal"),
    $("#prediction-modal").modal("show"),
    $("#upload-modal").modal("hide"),
    UnBlockUI()
}
