window.addEventListener("load", function () {
  // Masquer le loader
  const loader = document.getElementById("loader");
  const main = document.getElementById("main");
  if (loader) {
    loader.style.opacity = "0";
    loader.style.zIndex = "-1";
  }
  if (main) {
    main.style.opacity = "1";
  }
});
