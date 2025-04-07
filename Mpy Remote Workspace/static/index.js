import { makeFetchRequest, openModal, speaker, getTitle, updateTitle, scrollNavbarColor, updateGpio } from "./js-files/utils.js";
import { checkpoint, addChkpts } from "./js-files/gestionCheckpoint.js";
import { miseEnService, autoServiceTime, initialAutoServiceTime } from "./js-files/gestionSurveillance.js"
import { createHistorique } from "./js-files/historique.js";


document.addEventListener("DOMContentLoaded", async function () {
  const fetchAllData = async () => {
    try {
      const responseAll = await makeFetchRequest("/getAllData", {
        method: "GET",
      });
      const { dataChkpts, gpioDispo, surveillance, options, memory } = responseAll;
      // console.log(responseAll);
      return { dataChkpts, gpioDispo, surveillance, options, memory };
    } catch (error) {
      console.error("Erreur lors de la récupération des données :", error);
      // Gérer l'erreur ici (par exemple, afficher un message d'erreur à l'utilisateur)
      return null; // Ou une valeur par défaut selon votre besoin
    }
  };
  const { dataChkpts, gpioDispo, surveillance, options, memory } = await fetchAllData()
  console.log('memory')
  document.getElementById('memory').textContent = memory;
  //LogOut
  const logout = document.querySelector("#logout");
  logout.addEventListener("click", () => {
    window.location.href = "/logout";
  });
  // OUVERTURE MODAL
  openModal("#supprimer", "#modal-supprimer");
  openModal("#edit-title", "#modal-title");
  openModal("#ajouter", "#modal-ajouter");
  openModal("#modifier", "#modal-modifier");

  // ANNULER MODAL
  const allAnnulerModal = document.querySelectorAll(".annuler");
  const close = (modal) => {
    const closed = document.querySelector(`#${modal}`);
    closed.close();
  };

  allAnnulerModal.forEach((annulerModal) => {
    annulerModal.addEventListener("click", (e) => {
      e.preventDefault();
      close(e.target.getAttribute("data-id"));
      // console.log(e.target.getAttribute("data-id"));
    });
  });

  // ALERTE SONORE
  // console.log(dataChkpts)
  /* localStorage.setItem("speak", JSON.stringify(!options.speak));
  const speak = document.querySelector("#speak");
  speak.checked = !options.speak; */
  speaker(options.speak);
  // GESTION DU TITRE
  getTitle(options.title);
  updateTitle();
  // HISTORIQUE
  createHistorique();
  // CREATION DES CHECKPOINTS
  checkpoint(dataChkpts);
  updateGpio(gpioDispo);
  // GESTION BOUTON MISE EN SERVICE
  miseEnService(surveillance);
  // GESTION COULEUR BOUTON NAVBAR
  scrollNavbarColor();
  // AJOUTER UN CHECKPOINT
  addChkpts();
  const sectionAccueil = document.querySelector("#accueil");
  sectionAccueil.style.opacity = "1";
  const sectionOptions = document.querySelector("#options");
  sectionOptions.style.opacity = "1";
  initialAutoServiceTime(options);
  autoServiceTime();

  const arrow = document.querySelector("#arrow-collaps");
  const allIconBtn = document.querySelectorAll("#form-auto ion-icon");

  arrow.addEventListener("click", () => {
    const arrow = document.querySelector("#arrow-collaps");
    arrow.classList.toggle("rotate");
    const contentCollaps = document.querySelector(".content-collaps");
    contentCollaps.classList.toggle("visible");
    const btn = document.querySelector(".label-auto .boutton-switch");
    btn.classList.toggle("hidden");
  });

});
