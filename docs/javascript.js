var title = document.getElementsByClassName("title");
var background = document.getElementById("background");
var innerHeaders = document.getElementsByClassName("innerHeader");

const rootElement = document.documentElement;
rootElement.style.setProperty('--cWidth', '100vw');
rootElement.style.setProperty('--cHeight', '102vh');
rootElement.style.setProperty('--maximized', '1');

for (var i = 0; i < title.length; i++) {
    title[i].addEventListener("click", function(){
        window.location = "https://github.com/Nissyyy04/NVR-Editor";
    });
}

for (var i = 0; i < innerHeaders.length; i++) {
    innerHeaders[i].addEventListener("click", function () {
        const rootElement = document.documentElement;

        // Retrieve the current value of `--maximized`
        const maximized = getComputedStyle(rootElement).getPropertyValue('--maximized').trim();

        // Toggle between states
        if (maximized === '0') {
            rootElement.style.setProperty('--cWidth', '100vw');
            rootElement.style.setProperty('--cHeight', '102vh');
            rootElement.style.setProperty('--maximized', '1');
        } else if (maximized === '1') {
            rootElement.style.setProperty('--cWidth', '70vw');
            rootElement.style.setProperty('--cHeight', '70vh');
            rootElement.style.setProperty('--maximized', '0');
        } else {
        }
    });
}


var githubButton = document.getElementById("githubButton");
githubButton.addEventListener("click", function(){
    window.location = "https://github.com/Nissyyy04/NVR-Editor";
});

var docsButton = document.getElementById("docsButton");
docsButton.addEventListener("click", function(){
    window.location = "https://github.com/Nissyyy04/NVR-Editor/blob/main/README.md";
}); 

