const pathInput = document.querySelector(".path-input");
const dataDiv = document.querySelector(".data-div");

let searchTimer = null;
let searchAbortController = null;


const folderPath = dataDiv.dataset.folderPath;

const fullPath = folderPath.slice(1).split("/");
fullPath[0] = "Home";

pathInput.value = fullPath.join(" / ");

// const search = document.querySelector("input");


// focus
pathInput.addEventListener("focus", async (e) => {
    pathInput.value = folderPath;
});

// input
pathInput.addEventListener("input", async (e) => {
    // const value = pathInput.value.trim();

    // clearTimeout(searchTimer);

    // if (searchAbortController) {
    //     searchAbortController.abort();
    //     searchAbortController = null;
    // }

    // if (value.length <= 1) return;

    // searchTimer = setTimeout(async () => {
    //     const folders = await searchFolders(value);
    //     console.log(folders);
    // }, 400);
});

pathInput.addEventListener("keydown", async (e) => {
    // if (e.code === "Enter") {
    //     let value = pathInput.value.trim();

    //     if (value.at(-1) === "/") {
    //         value = value.slice(0, -1);
    //     }

    //     const response = await getFolder(value);
    //     if (response.status !== 200) {
    //         alert("This folder doesn't exists");
    //         return;
    //     }  // catch error

    //     const folder = await response.json();
    //     window.location.href = `/folders/${folder.id}`;
    // }
});

// blur
pathInput.addEventListener("blur", async (e) => {
    pathInput.value = fullPath.join(" / ");
});