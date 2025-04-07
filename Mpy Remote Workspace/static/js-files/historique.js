import { makeFetchRequest } from "./utils.js";

const colorTag = {
  green: "tag-green",
  red: "tag-red",
  blue: "tag-blue",
};
const icones = {
  buzz: '<ion-icon name="megaphone-outline" class="icon-card"></ion-icon>',
  alert: '<ion-icon name="warning-outline" class="icon-card"></ion-icon>',
  mes: '<ion-icon name="shield-checkmark-outline" class="icon-card"></ion-icon>',
  mhs: '<ion-icon name="shield-outline" class="icon-card"></ion-icon>',
  close: '<ion-icon name="lock-closed-outline" class="icon-card"></ion-icon>',
  open: ' <ion-icon name="lock-open-outline" class="icon-card"></ion-icon>',
  son: ' <ion-icon name="volume-high-outline" class="icon-card"></ion-icon>',
  mute: ' <ion-icon name="volume-mute-outline" class="icon-card"></ion-icon>',
  del: ' <ion-icon name="trash-outline" class="icon-card"></ion-icon>',
  add: ' <ion-icon name="add-circle-outline" class="icon-card"></ion-icon>',
  up: ' <ion-icon name="build-outline" class="icon-card"></ion-icon>',
  time: '<ion-icon name="time-outline" class="icon-card"></ion-icon>',
  finger: '<ion-icon name="finger-print-outline" class="icon-card"></ion-icon>',
};

const createElementHisto = (element) => {
  return document.createElement(element);
};

export const createHistorique = async () => {
  const fetchData = async () => {
    const data = await makeFetchRequest("/getHistorique", {
      method: "GET",
    });
    return data;
  };
  const historique = await fetchData();
  const fragment = document.createDocumentFragment();
  const container = document.querySelector("#view-historique");
  container.innerHTML = "";
  historique.reverse().map((data) => {
    const card = createElementHisto("div");
    card.className = "card-historique";

    const wrapperTag = createElementHisto("div");
    wrapperTag.className = `wrapper-tag ${colorTag[data[0].color]}`;

    const wrapperTxt = createElementHisto("div");
    wrapperTxt.className = "wrapper-txt";

    const pDate = createElementHisto("p");
    const pTxt = createElementHisto("p");
    wrapperTxt.append(pDate, pTxt);

    card.append(wrapperTag, wrapperTxt);

    wrapperTag.innerHTML = icones[data[0].iconeName];
    pDate.textContent = data[1];
    pTxt.innerHTML = data[2];

    const hr = createElementHisto("hr");
    fragment.append(card, hr);

    container.append(fragment);
  });
  const section = document.querySelector("#historique");
  section.style.opacity = "1";
};

export const updateHistorique = async () => {
  const fetchData = async () => {
    const data = await makeFetchRequest("/getLastHistorique", {
      method: "GET",
    });

    return data;
  };
  const { lastHistorique } = await fetchData();

  const fragment = document.createDocumentFragment();
  const container = document.querySelector("#view-historique");

  const card = createElementHisto("div");
  card.className = "card-historique";

  const wrapperTag = createElementHisto("div");
  wrapperTag.className = `wrapper-tag ${colorTag[lastHistorique[0].color]}`;

  const wrapperTxt = createElementHisto("div");
  wrapperTxt.className = "wrapper-txt";

  const pDate = createElementHisto("p");
  const pTxt = createElementHisto("p");
  wrapperTxt.append(pDate, pTxt);

  card.append(wrapperTag, wrapperTxt);

  wrapperTag.innerHTML = icones[lastHistorique[0].iconeName];
  pDate.textContent = lastHistorique[1];
  pTxt.innerHTML = lastHistorique[2];

  const hr = createElementHisto("hr");
  fragment.append(card, hr);

  container.prepend(fragment);
};
