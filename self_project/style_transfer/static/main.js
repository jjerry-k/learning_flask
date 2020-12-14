//========================================================================
// Drag and drop image handling
//========================================================================

var fileDrag = document.getElementById("file-drag");
var fileSelect = document.getElementById("file-upload");
var contentfileDrag = document.getElementById("content-drag");
var contentfileSelect = document.getElementById("content-upload");

// Add event listeners
fileDrag.addEventListener("dragover", fileDragHover, false);
fileDrag.addEventListener("dragleave", fileDragHover, false);
fileDrag.addEventListener("drop", fileSelectHandler, false);
fileSelect.addEventListener("change", fileSelectHandler, false);

contentfileDrag.addEventListener("dragover", contentfileDragHover, false);
contentfileDrag.addEventListener("dragleave", contentfileDragHover, false);
contentfileDrag.addEventListener("drop", contentfileSelectHandler, false);
contentfileSelect.addEventListener("change", contentfileSelectHandler, false);

function fileDragHover(e) {
  // prevent default behaviour
  e.preventDefault();
  e.stopPropagation();

  fileDrag.className = e.type === "dragover" ? "upload-box dragover" : "upload-box";
}

function fileSelectHandler(e) {
  // handle file selecting
  var files = e.target.files || e.dataTransfer.files;
  fileDragHover(e);
  for (var i = 0, f; (f = files[i]); i++) {
    previewFile(f);
  }
}

function contentfileDragHover(e) {
  // prevent default behaviour
  e.preventDefault();
  e.stopPropagation();

  contentfileDrag.className = e.type === "dragover" ? "upload-box dragover" : "upload-box";
}

function contentfileSelectHandler(e) {
  // handle file selecting
  var files = e.target.files || e.dataTransfer.files;
  contentfileDragHover(e);
  for (var i = 0, f; (f = files[i]); i++) {
    contentpreviewFile(f);
  }
}

//========================================================================
// Web page elements for functions to use
//========================================================================

var imagePreview = document.getElementById("image-preview");
var contentimagePreview = document.getElementById("content-image");
var imageDisplay = document.getElementById("image-display");
var uploadCaption = document.getElementById("upload-caption");
var contentCaption = document.getElementById("content-caption");
var predResult = document.getElementById("pred-result");
var loader = document.getElementById("loader");

//========================================================================
// Main button events
//========================================================================

function submitImage() {
  // action for the submit button
  console.log("submit");

  if (!imageDisplay.src || !imageDisplay.src.startsWith("data")) {
    window.alert("Please select an image before submit.");
    return;
  }

  loader.classList.remove("hidden");
  imageDisplay.classList.add("loading");

  // call the predict function of the backend
  predictImage(imageDisplay.src);
}

function clearImage() {
  // reset selected files
  fileSelect.value = "";

  // remove image sources and hide them
  imagePreview.src = "";
  contentimagePreview.src = "";
  imageDisplay.src = "";
  predResult.innerHTML = "";

  hide(imagePreview);
  hide(contentimagePreview);
  hide(imageDisplay);
  hide(loader);
  hide(predResult);
  show(uploadCaption);
  show(contentCaption);

  imageDisplay.classList.remove("loading");
}

function previewFile(file) {
  // show the preview of the image
  console.log(file.name);
  var fileName = encodeURI(file.name);

  var reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onloadend = () => {
    imagePreview.src = URL.createObjectURL(file);

    show(imagePreview);
    hide(uploadCaption);

    // reset
    predResult.innerHTML = "";
    imageDisplay.classList.remove("loading");

    displayImage(reader.result, "image-display");
  };
}

function contentpreviewFile(file) {
  // show the preview of the image
  console.log(file.name);
  var fileName = encodeURI(file.name);

  var reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onloadend = () => {
    // imagePreview.src = URL.createObjectURL(file);
    contentimagePreview.src = URL.createObjectURL(file);

    // show(imagePreview);
    show(contentimagePreview);
    hide(contentCaption);

    // reset
    predResult.innerHTML = "";
    imageDisplay.classList.remove("loading");

    displayImage(reader.result, "image-display");
  };
}

//========================================================================
// Helper functions
//========================================================================

function predictImage(image) {
  fetch("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(image)
  })
    .then(resp => {
      if (resp.ok)
        resp.json().then(data => {
          displayResult(data);
        });
    })
    .catch(err => {
      console.log("An error occured", err.message);
      window.alert("Oops! Something went wrong.");
    });
}

function displayImage(image, id) {
  // display image on given id <img> element
  let display = document.getElementById(id);
  display.src = image;
  show(display);
}

function displayResult(data) {
  // display the result
  // imageDisplay.classList.remove("loading");
  hide(loader);
  predResult.innerHTML = data.result;
  show(predResult);
}

function hide(el) {
  // hide an element
  el.classList.add("hidden");
}

function show(el) {
  // show an element
  el.classList.remove("hidden");
}