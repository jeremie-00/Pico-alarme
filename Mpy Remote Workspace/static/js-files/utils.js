// import { makeFetchRequest } from "./makeFetch.js";
import { updateHistorique } from "./historique.js";

export async function makeFetchRequest(url, options) {
  try {
    const response = await fetch(url, options);
    if (response.ok) {
      return response.json();
    } else {
      throw new Error(
        "Erreur de requête : " + response.status + " " + response.statusText
      );
    }
  } catch (error) {
    handleRequestError(error);
  }
}
export function handleRequestError(error) {
  console.error("Erreur lors de la requête :", error);
}

// GESTION GPIO
export async function updateGpio(initialGpioDispo = null) {
  const getGpio = async () => {
    const data = await makeFetchRequest(`/getGpio`, {
      method: "GET",
    });
    return data.gpioDispo;
  };
  const gpioDispo = initialGpioDispo ? initialGpioDispo : await getGpio();
  const ajouterButton = document.querySelector("#ajouter");
  const choixGpioSelect = document.querySelectorAll("select[name='choixGpio']");
  choixGpioSelect.innerHTML = "";
  choixGpioSelect.forEach((select) => {
    select.innerHTML = "";
    gpioDispo.forEach((valeur) => {
      const optionElement = document.createElement("option");
      optionElement.value = valeur;
      optionElement.text = valeur;
      select.appendChild(optionElement);
    });
  });

  ajouterButtonDisabled();
}

//SPEAKER SPEAK
export const speaker = (optionSpeak) => {
  if ("speechSynthesis" in window) {
    speechSynthesis.cancel();
    speechSynthesis.getVoices();
  }


  localStorage.setItem("speak", JSON.stringify(optionSpeak));
  const speakButton = document.querySelector("#speak");
  speakButton.checked = optionSpeak;

  /* const getSpeak = async () => {
    const fetchIsSpeak = async () => {
      const { isSpeak } = await makeFetchRequest("/getSpeak", {
        method: "GET",
      });

      return isSpeak;
    };

    const isSpeak = await fetchIsSpeak();
    localStorage.setItem("speak", JSON.stringify(isSpeak));

    const speak = document.querySelector("#speak");
    speak.checked = isSpeak;
  };
  getSpeak(); */

  const fetchSpeak = async (value) => {
    const { success, rep } = await makeFetchRequest("/putSpeak", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ speak: value }),
    });
    if (success) {
      localStorage.setItem("speak", JSON.stringify(rep));
      updateHistorique();
    } else {
      alert("Activation de la synthèse vocale impossible");
      const speak = document.querySelector("#speak");
      speak.checked = success;
    }
  };

  const speak = document.querySelector("#speak");
  speak.addEventListener("click", async (e) => {
    await fetchSpeak(e.target.checked);
  });
};

export const speak = (message) => {
  const synth = window.speechSynthesis;
  // Créer un objet SpeechSynthesisUtterance avec le message
  const utterance = new SpeechSynthesisUtterance(message);
  // Parler
  synth.speak(utterance);
};


// GESTION DU TITRE
const getFormElements = () => {
  const formTitle = document.querySelector("#form-title");
  const titleInput = formTitle.querySelector("input[name='title']");
  const modalTitle = document.querySelector("#modal-title");
  const title = document.querySelector("#title");
  return { formTitle, titleInput, modalTitle, title };
};

const handleFormSubmit = async (e) => {
  e.preventDefault();
  const { formTitle, titleInput, modalTitle } = getFormElements();
  const FD = new FormData(formTitle);

  const formData = {
    title:
      FD.get("title").charAt(0).toUpperCase() +
      FD.get("title").slice(1).toLowerCase(),
  };

  const response = await makeFetchRequest(`/putTitle`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title: formData }),
  });

  if (response.success) {
    const { title } = getFormElements();
    title.textContent = formData.title;
    titleInput.value = "";
    titleInput.placeholder = formData.title;
    updateHistorique();
  } else {
    alert(`Modification du titre ${formData.title} impossible`);
  }
  modalTitle.close();
};

export async function updateTitle(e) {
  const { formTitle } = getFormElements();
  // Nettoyage et ajout de l'écouteur d'événements
  formTitle.removeEventListener("submit", handleFormSubmit);
  formTitle.addEventListener("submit", handleFormSubmit);
}

export const getTitle = (optionsTitle) => {
  const { formTitle, titleInput, title } = getFormElements();
  title.textContent = optionsTitle;
  titleInput.placeholder = optionsTitle;
};
/* export const getTitle = async () => {
  const data = await makeFetchRequest("/getTitle", {
    method: "GET",
  });
  const { formTitle, titleInput, title } = getFormElements();
  title.textContent = data.title;
  titleInput.placeholder = data.title;
}; */

//SCROLL NAV BARRE
export function scrollNavbarColor() {
  // NAVBAR SCROLL REPERE ICON
  let navLinks = document.querySelectorAll(".nav-link");
  let ticking = false;

  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(function () {
        let scrollPosition = window.scrollY;
        let windowHeight = window.innerHeight;
        // Parcourir les liens de navigation
        navLinks.forEach(function (link) {
          let sectionId = link.getAttribute("href").substring(1); // Obtenez l'ID de la section correspondante

          // Obtenez la section correspondante
          let section = document.getElementById(sectionId);
          let sectionTop = section.offsetTop;
          let sectionBottom = sectionTop + section.offsetHeight;

          // Vérifiez si la section est entièrement visible à l'écran
          if (scrollPosition <= 10) {
            // Si on est tout en haut de la page, activez le premier lien
            if (sectionId === navLinks[0].getAttribute("href").substring(1)) {
              link.classList.add("active");
            } else {
              link.classList.remove("active");
            }
          } else if (
            scrollPosition <= sectionTop &&
            sectionBottom <= scrollPosition + windowHeight
          ) {
            // Ajoutez la classe active au lien de navigation correspondant
            link.classList.add("active");
          } else {
            // Supprimez la classe active si la section n'est pas entièrement visible
            link.classList.remove("active");
          }
        });
        ticking = false;
      });
      ticking = true;
    }
  }

  window.addEventListener("scroll", onScroll);
}

//MODAL
export function createItemModalList(data, action, icon) {
  const fragment = document.createDocumentFragment();
  const cardList = document.createElement("div");
  cardList.className = "card-list";

  const wrapper = document.createElement("div");
  wrapper.className = "wrapper-list";
  const p = document.createElement("p");
  p.setAttribute("data-name", data.id);
  p.textContent = data.name;
  wrapper.appendChild(p);

  const button = document.createElement("button");
  button.setAttribute("data-id", data.id);
  button.setAttribute("data-confirm", data.name);
  button.className = "boutton-carre clickable";
  button.innerHTML = icon;

  // Créez un span pour les lecteurs d'écran
  const srLabel = document.createElement("span");
  srLabel.className = "sr-only";
  srLabel.textContent = `Action for ${data.name}`; // Texte descriptif pour les lecteurs d'écran
  button.appendChild(srLabel);

  button.addEventListener("click", action);
  cardList.append(wrapper, button);
  const hr = document.createElement("hr");
  fragment.append(cardList, hr);

  return fragment;
}

export function openModal(buttonSelector, modalSelector) {
  const button = document.querySelector(buttonSelector);
  const modal = document.querySelector(modalSelector);
  if (button && modal) {
    button.addEventListener("click", () => {
      modal.showModal();
    });
  }
}

//BOUTON OPTION MASQUAGE
const getElements = () => {
  return {
    modifier: document.querySelector("#modifier"),
    supprimer: document.querySelector("#supprimer"),
    ajouter: document.querySelector("#ajouter"),
    switchMES: document.querySelector("#switch"),
    choixGpioSelect: document.querySelector(
      "#modal-ajouter select[name='choixGpio']"
    ),
  };
};

export const disabledButtonOptions = (value) => {
  const { modifier, supprimer } = getElements();
  modifier.disabled = value;
  supprimer.disabled = value;
  ajouterButtonDisabled();
};

export const ajouterButtonDisabled = () => {
  const { choixGpioSelect, ajouter, switchMES } = getElements();
  ajouter.disabled = switchMES.checked || choixGpioSelect.length === 0;
};