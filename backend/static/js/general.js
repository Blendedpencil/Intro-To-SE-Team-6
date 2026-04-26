const images = document.getElementsByTagName("img");
const text = document.getElementById("text");

for (let i = 0; i < images.length; i++) {
images[i].addEventListener("mouseover", function() {
text.textContent = this.alt;
});
images[i].addEventListener("mouseleave", function() {
text.textContent = "";
});
}