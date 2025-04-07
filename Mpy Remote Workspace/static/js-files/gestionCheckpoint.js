import { makeFetchRequest, updateGpio, createItemModalList, ajouterButtonDisabled } from "./utils.js";
import { updateHistorique } from "./historique.js";

// CHECKPOINTS
const allCards = [];
export { allCards };

export async function checkpoint(dataChkpts = null) {
    const containerCheckpoints = document.querySelector("#sectionChkpts");
    //OBJET ICONE
    const icones = {
        fermer:
            ' <ion-icon name="lock-closed-outline" class="icon-card"></ion-icon>',
        ouvert: '<ion-icon name="lock-open-outline" class="icon-card"></ion-icon>',
        modifier: `<ion-icon name="build-outline"class="icon-card">`,
        supprimer: `<ion-icon name="trash-outline" class="icon-card"></ion-icon>`,
    };
    class Card {
        constructor(data) {
            this.name = data.name;
            this.message =
                data.state === 0 ? "La porte est fermée" : "La porte est ouverte";
            this.colorTag = data.state === 0 ? "tag-green" : "tag-red";
            this.icon = data.state === 0 ? icones.fermer : icones.ouvert;
            this.alarme = data.alarme ? true : false;
            this.date = data.alarme ? data.alarme.date : null;
            this.heure = data.alarme ? data.alarme.heure : null;
            this.id = data.id;
            this.gpio = data.gpio;
            this.potl = data.potl;
            this.chrono = data.chrono;
        }
        // CREATION DU CONTENEUR
        containerCard() {
            this.card = document.createElement("div");
            this.card.className = "card";
            this.card.setAttribute("data-id", this.id);
            this.wrapperTag = document.createElement("div");
            this.wrapperTag.className = `wrapper-tag ${this.colorTag}`;

            this.wrapperTxt = document.createElement("div");
            this.wrapperTxt.className = "wrapper-txt";
            this.h3 = document.createElement("h3");
            this.h3.setAttribute("data-name", this.id);
            this.p = document.createElement("p");
            this.messageAlarme = document.createElement("p");
            this.wrapperTxt.append(this.h3, this.p, this.messageAlarme);
            this.iconInfo = document.createElement("ion-icon");
            this.iconInfo.setAttribute("name", "information-circle-outline");
            this.iconInfo.className = "icon-card";

            this.card.append(this.wrapperTag, this.wrapperTxt, this.iconInfo);

            return this.card;
        }
        create() {
            this.h3.textContent = `${this.name}`;
            this.p.textContent = this.message;
            this.messageAlarme.innerHTML = this.alarme
                ? `Alarme à ${this.heure} </br> le ${this.date}`
                : "";
            this.wrapperTag.innerHTML = this.icon;

            this.card.addEventListener("click", () => {
                this.getInfo();
            });
        }
        update(data) {
            this.name = data.name;
            this.message =
                data.state === 0 ? "La porte est fermée" : "La porte est ouverte";
            this.colorTag = data.state === 0 ? "tag-green" : "tag-red";
            this.wrapperTag.className = `wrapper-tag ${this.colorTag}`;
            this.icon = data.state === 0 ? icones.fermer : icones.ouvert;
            this.alarme = data.alarme ? true : false;
            this.date = data.alarme ? data.alarme.date : null;
            this.heure = data.alarme ? data.alarme.heure : null;
            this.potl = data.potl;
            this.chrono = data.chrono;
            this.gpio = data.gpio;

            this.create();
        }
        getInfo() {
            const modalInfo = document.querySelector("#modal-info");
            const chkptInfo = modalInfo.querySelector(".chkpt-info");
            const closed = document.querySelector(".close-icon");
            const pNameInfo = document.createElement("p");
            pNameInfo.textContent = `Name: ${this.name}`;

            // Clear existing <p> elements
            const allP = modalInfo.querySelectorAll("p");
            allP.forEach((p) => p.remove());

            // Ajout des nouvelles balises <p> pour gpio, chrono et potl
            const pGpio = document.createElement("p");
            pGpio.textContent = `GPIO: ${this.gpio}`;
            const pPotl = document.createElement("p");
            pPotl.textContent = `POTL: ${this.potl ? "Oui" : "Non"}`;
            const pChrono = document.createElement("p");
            pChrono.textContent = `Chrono: ${this.chrono}`;

            // Ajout des éléments <p> au modal
            chkptInfo.appendChild(pNameInfo);
            chkptInfo.appendChild(pGpio);
            chkptInfo.appendChild(pPotl);
            chkptInfo.appendChild(pChrono);

            modalInfo.showModal();
            closed.addEventListener("click", () => {
                modalInfo.close();
            });
        }
    }

    const containerModalSupprimer = document.querySelector("#viewSupprimer");
    const containerModalModifier = document.querySelector("#viewModifier");

    const fetchData = async () => {
        const data = await makeFetchRequest("/getDataChkpts", {
            method: "GET",
        });
        return data;
    };

    const data = dataChkpts ? dataChkpts : await fetchData();

    data.map((d) => {
        const existingCard = allCards.find((card) => card.id === d.id);
        if (existingCard) {
            existingCard.update(d);
        } else {
            const card = new Card(d);
            containerCheckpoints.appendChild(card.containerCard());
            card.create(d);
            allCards.push(card);
            containerModalSupprimer.appendChild(
                createItemModalList(d, deleteChkpts, icones.supprimer)
            );
            containerModalModifier.appendChild(
                createItemModalList(d, updateChkpts, icones.modifier)
            );
        }
    });
    const section = document.querySelector("#portes");
    section.style.opacity = "1";
}

export function updateCheckpointIcon(data) {
    data.map((d) => {
        const existingCard = allCards.find((card) => card.id === d.id);
        existingCard.update(d);
    });
}


// ADD CHECKPOINTS
const handleFormSubmit = async (e) => {
    e.preventDefault();
    const formData = getFormData();
    const response = await makeFetchRequest(`/chkpts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ data: formData }),
    });

    // console.log(response);
    if (response.success) {
        document.querySelector("#form-ajouter input[name='name']").value = "";
        checkpoint();
        closeModal();
        updateHistorique();
        updateGpio();
    } else {
        alert(response.error);
    }
};

const getFormData = () => {
    const formAjouter = document.querySelector("#form-ajouter");
    const FD = new FormData(formAjouter);
    const surveillance = document.querySelector("#switch");
    let chrono = FD.get("chrono");
    if (chrono.length < 8) {
        chrono += ":00";
    }
    return {
        name: FD.get("name"),
        gpio: parseInt(FD.get("choixGpio")),
        id: null,
        alarme: null,
        surveillance: surveillance.checked,
        tasks: [],
        potl: FD.get("rdo") === "true",
        chrono: chrono,
    };
};

const closeModal = () => {
    const modalAjouter = document.querySelector("#modal-ajouter");
    modalAjouter.close();
};

const populateGpioOptions = async () => {
    const { gpioDispo } = await makeFetchRequest(`/getGpio`, { method: "GET" });
    const choixGpioSelect = document.querySelector(
        "#modal-ajouter select[name='choixGpio']"
    );
    choixGpioSelect.innerHTML = "";
    gpioDispo.forEach((valeur) => {
        const optionElement = document.createElement("option");
        optionElement.value = valeur;
        optionElement.text = valeur;
        choixGpioSelect.appendChild(optionElement);
    });
};

export async function addChkpts(e) {
    //updateGpio();
    const modalAjouter = document.querySelector("#modal-ajouter");
    modalAjouter.removeEventListener("submit", handleFormSubmit);
    modalAjouter.addEventListener("submit", handleFormSubmit);
}

// DELETE CHECKPOINTS
export async function deleteChkpts(e) {
    const modalSupprimer = document.querySelector("#modal-supprimer");
    const allChkpts = document.querySelectorAll(".card");
    const allChkptsModal = document.querySelectorAll(".boutton-carre");

    const { id, name, parentModal } = getTargetDetails(e);

    if (!id || !name) {
        console.error("ID ou nom non trouvé.");
        return;
    }

    const userConfirmed = confirm(`Voulez-vous vraiment supprimer ${name} ?`);

    if (userConfirmed) {
        try {
            const { success } = await deleteCheckpoint(id);
            if (success) {
                removeElementsFromDOM(id, allChkpts, allChkptsModal, parentModal);
                modalSupprimer.close();
                updateHistorique();
                updateGpio();
                ajouterButtonDisabled();
            } else {
                console.error("ID ou nom non trouvé.");
            }
        } catch (error) {
            console.error("Erreur lors de la suppression du checkpoint :", error);
        }
    } else {
        console.log("L'utilisateur a annulé la suppression.");
    }
}

function getTargetDetails(e) {
    let id = null;
    let name = null;
    let parentModal = null;

    if (e.target.tagName.toLowerCase() === "ion-icon") {
        const parentButton = e.target.closest(".boutton-carre");
        parentModal = e.target.closest(".card-list");

        if (parentButton) {
            id = parentButton.getAttribute("data-id");
            name = parentButton.getAttribute("data-confirm");
        }
    } else {
        parentModal = e.target.closest(".card-list");
        id = e.target.getAttribute("data-id");
        name = e.target.getAttribute("data-confirm");
    }

    return { id, name, parentModal };
}

async function deleteCheckpoint(id) {
    const response = await makeFetchRequest(`/chkpts/${id}`, {
        method: "DELETE",
    });
    if (!response.success) {
        throw new Error(`Erreur HTTP ! statut : ${response.succes}`);
    }
    return response;
}

function removeElementsFromDOM(id, allChkpts, allChkptsModal, parentModal) {
    allChkptsModal.forEach((chkpts) => {
        if (chkpts.getAttribute("data-id") === id) {
            const parent = chkpts.closest(".card-list");
            const hrElement = parent.nextElementSibling;
            if (hrElement) {
                hrElement.remove();
            }
            parent.remove();
        }
    });

    allChkpts.forEach((chkpts) => {
        if (chkpts.getAttribute("data-id") === id) {
            chkpts.remove();
        }
    });

    if (parentModal) {
        parentModal.remove();
    }
}

// UPDATE CHECKPOINTS
const getElements = () => {
    const formModification = document.querySelector("#form-modification");
    return {
        modalmodification: document.querySelector("#modal-modification"),
        formModification: formModification,
        allName: document.querySelectorAll("[data-name]"),
        modalModifier: document.querySelector("#modal-modifier"),
        nameTitle: document.querySelector(".name-title"),
        nameInput: formModification.querySelector("input[name='name']"),
        choixGpioSelect: formModification.querySelector("select[name='choixGpio']"),
        chronoInput: formModification.querySelector("input[name='chrono']"),
    };
};

const handleFormSubmitUpdate = async (e) => {
    e.preventDefault();
    const { modalmodification, formModification, allName } = getElements();
    const FD = new FormData(formModification);

    const formData = {
        name: FD.get("name"),
        gpio: parseInt(FD.get("choixGpio")),
        potl: FD.get("rdo") === "true",
        chrono: FD.get("chrono"),
    };
    if (formData.chrono.length < 8) {
        formData.chrono += ":00";
    }
    const id = formModification.getAttribute("data-id");
    const response = await makeFetchRequest(`/chkpts/${id}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ data: formData }),
    });
    if (response.success) {
        allName.forEach((name) => {
            const dataName = parseInt(name.getAttribute("data-name"));
            if (dataName === parseInt(id)) {
                name.textContent = formData.name;
            }
        });
        checkpoint();
        updateHistorique();
        updateGpio();
    } else {
        alert(`Modification du point de controle ${formData.name} impossible`);
    }
    modalmodification.close();
};

export async function updateChkpts(e) {
    const {
        modalmodification,
        modalModifier,
        formModification,
        nameTitle,
        nameInput,
        choixGpioSelect,
        chronoInput,
    } = getElements();

    let id = null;
    let parentModal = null;
    if (e.target.tagName.toLowerCase() === "ion-icon") {
        const parentButton = e.target.closest(".boutton-carre");
        parentModal = e.target.closest(".card-list");

        if (parentButton) {
            id = parentButton.getAttribute("data-id");
        }
    } else {
        parentModal = e.target.closest(".card-list");
        id = e.target.getAttribute("data-id");
    }

    const getUpdateChkpts = async () => {
        const data = await makeFetchRequest(`/chkpts/${id}`, {
            method: "GET",
        });
        return data;
    };

    const { data, gpioDispo } = await getUpdateChkpts();

    nameInput.value = data.name;
    nameTitle.textContent = data.name;
    choixGpioSelect.innerHTML = "";
    const optionElementDefault = document.createElement("option");
    optionElementDefault.value = data.gpio;
    optionElementDefault.text = data.gpio;
    optionElementDefault.style.color = "black";
    optionElementDefault.style.fontWeight = "bold";
    choixGpioSelect.appendChild(optionElementDefault);

    gpioDispo.forEach((valeur) => {
        const optionElement = document.createElement("option");
        optionElement.value = valeur;
        optionElement.text = valeur;
        choixGpioSelect.appendChild(optionElement);
    });

    chronoInput.value = data.chrono;
    if (data.potl) {
        const potlInput = formModification.querySelector("#yes-modification");
        potlInput.checked = true;
    } else {
        const potlInput = formModification.querySelector("#no-modification");
        potlInput.checked = true;
    }

    modalModifier.close();
    modalmodification.showModal();

    const name = nameInput.value;
    let choixGpio = "";
    choixGpioSelect.addEventListener("change", function (e) {
        choixGpio = e.target.value;
    });

    formModification.setAttribute("data-id", id);

    // Nettoyage et ajout de l'écouteur d'événements
    formModification.removeEventListener("submit", handleFormSubmitUpdate);
    formModification.addEventListener("submit", handleFormSubmitUpdate);
}
