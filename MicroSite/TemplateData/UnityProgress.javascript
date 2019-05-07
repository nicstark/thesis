function UnityProgress(gameInstance, progress) {
  if (!gameInstance.Module)
    return;
  if (!gameInstance.logo) {
    gameInstance.logo = document.createElement("div");
    gameInstance.logo.className = "logo " + gameInstance.Module.splashScreenStyle;
    gameInstance.container.appendChild(gameInstance.logo);
  }
  if (!gameInstance.progress) {
    gameInstance.progress = document.createElement("div");
    gameInstance.progress.className = "progress " + gameInstance.Module.splashScreenStyle;
    gameInstance.progress.loadText = document.createElement("div");
    gameInstance.progress.loadText.className = "load-text";
    gameInstance.progress.loadText.innerHTML = "Cambrian Analytica is Loading";
    gameInstance.progress.loadAnimation = document.createElement("div");
    gameInstance.progress.loadAnimation.className = "sk-circle";
    gameInstance.progress.loaderDiv1 = document.createElement('div');
    gameInstance.progress.loaderDiv1.className = "sk-circle1 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv1);
    gameInstance.progress.loaderDiv2 = document.createElement('div');
    gameInstance.progress.loaderDiv2.className = "sk-circle2 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv2);
    gameInstance.progress.loaderDiv3 = document.createElement('div');
    gameInstance.progress.loaderDiv3.className = "sk-circle3 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv3);
    gameInstance.progress.loaderDiv4 = document.createElement('div');
    gameInstance.progress.loaderDiv4.className = "sk-circle4 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv4);
    gameInstance.progress.loaderDiv5 = document.createElement('div');
    gameInstance.progress.loaderDiv5.className = "sk-circle5 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv5);
    gameInstance.progress.loaderDiv6 = document.createElement('div');
    gameInstance.progress.loaderDiv6.className = "sk-circle6 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv6);
    gameInstance.progress.loaderDiv7 = document.createElement('div');
    gameInstance.progress.loaderDiv7.className = "sk-circle7 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv7);
    gameInstance.progress.loaderDiv8 = document.createElement('div');
    gameInstance.progress.loaderDiv8.className = "sk-circle8 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv8);
    gameInstance.progress.loaderDiv9 = document.createElement('div');
    gameInstance.progress.loaderDiv9.className = "sk-circle9 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv9);
    gameInstance.progress.loaderDiv10 = document.createElement('div');
    gameInstance.progress.loaderDiv10.className = "sk-circle10 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv10);
    gameInstance.progress.loaderDiv11 = document.createElement('div');
    gameInstance.progress.loaderDiv11.className = "sk-circle11 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv11);
    gameInstance.progress.loaderDiv12 = document.createElement('div');
    gameInstance.progress.loaderDiv12.className = "sk-circle12 sk-child";
    gameInstance.progress.loadAnimation.appendChild(gameInstance.progress.loaderDiv12);
    gameInstance.progress.appendChild(gameInstance.progress.loadText)
    gameInstance.progress.appendChild(gameInstance.progress.loadAnimation)
    gameInstance.container.appendChild(gameInstance.progress);
  }
  if (progress == 1)
    gameInstance.logo.style.display = gameInstance.progress.style.display = "none";
}
