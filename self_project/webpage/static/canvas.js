const canvas = document.getElementById("jsCanvas");
const range_control = document.getElementById("jsRange");
const color_control = document.getElementsByClassName("jsColor");
const fill_mode = document.getElementById("jsMode");
const save_btn = document.getElementById("jsSave");
const ctx = canvas.getContext('2d');

const INIT_COLOT = "#2c2c2c"
const CANVAS_SIZE = 700;

canvas.width = CANVAS_SIZE;
canvas.height = CANVAS_SIZE;

ctx.fillStyle = "white";
ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

ctx.strokeStyle = INIT_COLOT;
ctx.lineWidth = 2.5;
ctx.fillStyle = INIT_COLOT;

let painting = false;
let filling = false;

function startPainting(){
    painting = true;
}

function stopPainting(){
    painting = false;
}

function onMouseMove(event){
    const x = event.offsetX;
    const y = event.offsetY;
    if(!painting){
        ctx.beginPath();
        ctx.moveTo(x, y);
        // console.log("Move", x, y);
    } else{
        ctx.lineTo(x, y);
        ctx.stroke();
    }
}

function handleCanvasClick(){
    if(filling===true){
        ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    }
}

function handleCM(event){
    event.preventDefault();
}

if(canvas){
    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mousedown", startPainting);
    canvas.addEventListener("mouseup", stopPainting);
    canvas.addEventListener("mouseleave", stopPainting);
    canvas.addEventListener("click", handleCanvasClick);
    canvas.addEventListener("contextmenu", handleCM);
}

// Handle Color
function handleColor(event){
    ctx.strokeStyle = event.target.style.backgroundColor;
    ctx.fillStyle = event.target.style.backgroundColor;
}

Array.from(color_control).forEach(color => 
    color.addEventListener("click", handleColor)
    );

// Handle Brush size
function handleBrushSize(event){
    ctx.lineWidth = event.target.valueAsNumber;
}

if(range_control){
    range_control.addEventListener("input", handleBrushSize);
}

// Handle Filling mode
function handleFillingMode(event){
    if(filling===true){
        filling = false;    
        fill_mode.innerText = "Stroke";
    } else{
        filling = true;
        fill_mode.innerText = "Fill";
    }
}

if(fill_mode){
    fill_mode.addEventListener("click", handleFillingMode);
}

function saveImage(event){
    const image = canvas.toDataURL("image/jpeg");
    const link = document.createElement("a");
    link.href = image;
    link.download = "PaintJS[🎨]";
    link.click();
    console.log(link);
}

if(save_btn){
    save_btn.addEventListener("click", saveImage);
}