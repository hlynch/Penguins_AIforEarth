function render() {
    Initialize(), UploadLinkClick(), FileUploadOnChange(), SearchSubmit(), SearchEnterKeyPressed()
}

function Initialize() {
    -1 == window.location.pathname.split("/")[1].indexOf("about"),
    $("#upload-modal-container").load("/static/static-templates/upload_modal.html"),
    $("#prediction-modal-container").load("/static/static-templates/prediction_modal.html")
}

function BlockUI(e) {
    UnBlockUI();
    var o = $(document).height(),
        i = "<div id='loader'></div><div id='overlay'></div>";
    e && (i = "<div id='loader'></div><div id='additional-loading-msg'></div><div id='overlay'></div>"), $("body").append(i), $("#overlay").height(o).css({
        opacity: .7,
        position: "absolute",
        top: 0,
        left: 0,
        "background-color": "black",
        width: "100%",
        "z-index": 5e3
    })
}

function UnBlockUI() {
    $("#overlay").remove(), $("#loader").remove(), $("#additional-loading-msg").remove()
}

function SampleImagePredictBtnClick(e) {
    var o = $(e).find("img").attr("src");
    GetImagePrediction(PredictionType.SampleImage, o)
}

function InputUrlClick(e) {
    $("#file-input").val(""), $(e).val("")
}

function ProgressLoadingMsgs(e) {
    el = $("#additional-loading-msg"), el.html(e)
}
$(window).ready(render), window.onerror = function(e, o, i) {
    return alert("An error occured, please check console for details"), console.log(e), !1
};