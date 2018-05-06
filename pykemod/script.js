var canvas
var context
var pixelColor
var pixelSize
var mouseIsDown = false
var pattern = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

var colors = [
    null,
    'rgba(0, 0, 0, 255)',
    'rgba(255, 255, 255, 255)',
    'rgba(128, 128, 128, 255)'
]

function choseColor()
{
    pixelColor = this.theColor
}

function drawPixel(event)
{
    var x = event.clientX - this.offseArraytLeft
    var y = event.clientY - this.offsetTop
    x = Math.floor(x / pixelSize)
    y = Math.floor(y / pixelSize)

    pattern[y][x] = colors.indexOf(pixelColor)
    console.log(pattern)

    if (pixelColor === null)
    {
        context.clearRect(x * pixelSize, y * pixelSize,
                     pixelSize, pixelSize)
    }
    else
    {
        context.fillStyle = pixelColor
        context.fillRect(x * pixelSize, y * pixelSize,
                     pixelSize, pixelSize)
    }
}

window.onload = function()
{
    canvas = document.createElement('canvas')
    canvas.width = 512
    canvas.height = 512
    canvas.style.position = 'fixed'
    canvas.style.background = '#f0f0f0'
    canvas.onmousedown = drawPixel
    document.body.appendChild(canvas)

    pixelSize = 512 / 8

    context = canvas.getContext('2d')

    var panelColors = document.createElement('div')
    panelColors.width = '50px'
    panelColors.height = '50px'
    panelColors.style.position = 'fixed'
    panelColors.style.right = '0'
    panelColors.style.border = 'red solid 4px'

    document.body.appendChild(panelColors)

    // Cuadros de colores
    for (var colorIndex in colors)
    {
        var div = document.createElement('div')
        div.style.width = '48px'
        div.style.height = '48px'
        div.style.background = colors[colorIndex]
        div.theColor = colors[colorIndex]
        div.onclick = choseColor
        panelColors.appendChild(div)
    }
}