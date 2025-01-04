var title = document.getElementsByClassName("title");
var background = document.getElementById("background");

for (var i = 0; i < title.length; i++) {
    title[i].addEventListener("click", function(){
        window.location = "https://github.com/Nissyyy04/NVR-Editor";
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

