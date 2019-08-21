var showBbox = !1
  , PredictionType = {
    SampleImage: 1,
    UploadedImage: 2
};

function GetImagePrediction(e, o) {
    switch (BlockUI(!0),
    setTimeout(function() {
        ProgressLoadingMsgs("Checking image dimensions...")
    }, 100),
    setTimeout(function() {
        ProgressLoadingMsgs("Resizing image...")
    }, 1e3),
    setTimeout(function() {
        ProgressLoadingMsgs("Sending image to API for prediction...")
    }, 1e3),
    e) {
    case PredictionType.SampleImage:
        //GetSampleImagePrediction(o); // TODO: no need to separate these
        GetImagePredictionUploadedFile(o)
        break;
    case PredictionType.UploadedImage:
        GetImagePredictionUploadedFile(o)
    }
}

function GetSampleImagePrediction(e) {
    $.ajax({
        url: "/get_sample_image_prediction",
        method: "GET",
        data: {
            imgPath: e,
            showbbox: showBbox
        }
    }).done(function(e) {
        PopulateModal(e.data, e.img_path)
    }).fail(function(e, o, i) {
        UnBlockUI(),
        e.getAllResponseHeaders() && (alert("An error occurred while predicting image  please check console for more details"),
        console.log("An error occurred while predicting image"),
        console.log("Error details:"),
        console.log(i))
    })
}

function GetImagePredictionUploadedFile(e) {
    console.log("GetImagePredictionUploadedFile"),
    PopulateModal(e.data, e.img_path),
    $("#upload-modal").modal("hide")
}

function PopulateModal(e, o) {
    console.log("populate modal"),
    //$(".modal img").attr("src", ""),
    ShowPredictionModal()
}

function ShowPredictionModal() {
    console.log("ShowPredictionModal"),
    $("#prediction-modal").modal("show"),
    $("#upload-modal").modal("hide"),
    UnBlockUI()
}
