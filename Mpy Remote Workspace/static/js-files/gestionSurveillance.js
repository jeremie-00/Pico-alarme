import { checkpoint } from "./gestionCheckpoint.js";
import { speak, makeFetchRequest, disabledButtonOptions } from "./utils.js";
import { updateHistorique } from "./historique.js";
// import { updateGpio } from "./updateGpio.js";

const titleAutoMode = (auto = null, bypass = null) => {
    const titlePlage = document.querySelector(".title-plage");
    titlePlage.textContent = bypass
        ? "Auto mode bypass"
        : auto ? "Auto mode" : "Plage horaire";
}

// MISE EN SERVICE
// BOUTTON MISE EN SERVICE API
export async function miseEnService(surveillance, optionsAutoModeBypass, optionsAuto) {
    const btnSurveillance = document.querySelector("#switch");

    const handleSurveillanceClick = async (e) => {
        speak("");
        const { success, value, message, autoModeBypass, auto } = await fetchSurveillance(
            e.target.checked
        );
        alert(message);
        titleAutoMode(auto, autoModeBypass)
        btnSurveillance.checked = value;
        disabledButtonOptions(value);
        handleSpeak(message);
        checkpoint();
        updateHistorique();
    };

    const fetchSurveillance = async (checked) => {
        const data = await makeFetchRequest("/patchSurveillance", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ surveillance: checked }),
        });
        return data;
    };

    const handleSpeak = (message) => {
        const isSpeak = JSON.parse(localStorage.getItem("speak"));
        if (isSpeak) speak(message);
    };

    btnSurveillance.addEventListener("click", handleSurveillanceClick);
    // RECUPERATION DES VALEUR DE MISE EN SERVICE API
    /* const fetchInitialSurveillanceState = async () => {
        const { success, autoModeBypass, auto } = await makeFetchRequest(
            "/getSurveillance",
            {
                method: "GET",
            }
        );

        // console.log(success, autoModeBypass, auto)
        const titlePlage = document.querySelector(".title-plage");
        titlePlage.textContent = autoModeBypass
            ? "Auto mode bypass"
            : auto ? "Auto mode" : "Plage horaire";
        return success;
    }; */

    titleAutoMode(optionsAuto, optionsAutoModeBypass)
    const initialResponse = surveillance //await fetchInitialSurveillanceState();
    btnSurveillance.checked = initialResponse;
    disabledButtonOptions(initialResponse);
}

// AUTOSURVEILLANCE
const handleFormSubmit = async (e) => {
    e.preventDefault();
    const FD = new FormData(e.target);
    const formData = {
        auto: FD.get("switch-auto") !== null,
        start: FD.get("start"),
        end: FD.get("end"),
    };
    if (formData.start.length === 8) formData.start = formData.start.slice(0, -3);
    if (formData.end.length === 8) formData.end = formData.end.slice(0, -3);
    const { success, isSurveillance } = await makeFetchRequest(
        `/patchAutoSurveillance`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ data: formData }),
        }
    );
    const btnSurveillance = document.querySelector("#switch");
    if (formData.auto) {
        btnSurveillance.checked = isSurveillance;
        disabledButtonOptions(isSurveillance);
    }
    titleAutoMode(formData.auto)
    if (success) {
        alert("Pris en charge ok");
    } else {
        alert("prise en charge non ok");
    }
};

export async function autoServiceTime(e) {
    const formAuto = document.querySelector("#form-auto");
    formAuto.removeEventListener("submit", handleFormSubmit);
    formAuto.addEventListener("submit", handleFormSubmit);
}

export async function initialAutoServiceTime(options) {
    // RECUPERATION DES VALEUR DE MISE EN SERVICE API
    /* const fetchInitialAutoServiceTime = async () => {
        const { data } = await makeFetchRequest("/getAutoSurveillance", {
            method: "GET",
        });

        return data;
    }; */

    const data = options //await fetchInitialAutoServiceTime();
    const formAuto = document.querySelector("#form-auto");
    // Assigner les valeurs aux champs du formulaire
    const autoCheckbox = formAuto.querySelector("#auto");
    const startInput = formAuto.querySelector("#start");
    const endInput = formAuto.querySelector("#end");

    // Remplir les champs du formulaire avec les valeurs récupérées
    autoCheckbox.checked = data.auto; // Cocher ou décocher la case en fonction de la valeur récupérée
    startInput.value = data.start;
    endInput.value = data.end;

    titleAutoMode(data.auto, data.autoModeBypass)
}
