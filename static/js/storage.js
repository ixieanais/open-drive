const backgroundWrapper = document.querySelector(".background-wrapper");
const backgroundContainer = document.querySelector(".background-container");
const dialogWrapper = document.querySelector(".dialog-wrapper");
const dialogWindow = dialogWrapper.querySelector(".dialog-window");

const gridContainer = document.querySelector(".grid-container");
const folders = document.querySelectorAll(".folders");
const files = document.querySelectorAll(".files");
const gridContextMenu = document.getElementById("grid-context-menu");
const foldersContextMenu = document.getElementById("folders-context-menu");
const filesContextMenu = document.getElementById("files-context-menu");
const fileInput = document.getElementById("fileInput");

const folderSVG = `
<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#789DE5">
    <path d="M166.78-140.78q-44.3 0-75.15-30.85-30.85-30.85-30.85-75.15v-466.44q0-44.3 30.85-75.15 30.85-30.85 75.15-30.85h224.74L480-730.74h313.22q44.3 0 75.15 30.85 30.85 30.85 30.85 75.15v377.96q0 44.3-30.85 75.15-30.85 30.85-75.15 30.85H166.78Z"/>
</svg>
`;

let selectedItem = null;
let contextItem = null;


function formatBytes(bytes, decimals = 2) {
    if (bytes === "0") return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const value = bytes / Math.pow(k, i);
    return value.toFixed(decimals) + " " + sizes[i];
}


function formatDate(isoDate) {
    const date = new Date(isoDate);
    const formatted = new Intl.DateTimeFormat("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
    }).format(date);

    return formatted
}


function renderItemInformation(item) {
    setTimeout(() => {
        const itemInfo = document.createElement("div");
        itemInfo.className = "item-information";
        const span = document.createElement("span");
        spanText = `"${item.innerText}" selected (${formatBytes(item.dataset.size)})`;
        if (item.dataset.itemType === "folder") spanText = `"${item.innerText}" selected`;
        span.textContent = spanText;
        itemInfo.appendChild(span);
        document.querySelector(".storage-wrapper").appendChild(itemInfo);
    }, 200)
}


function unrenderItemInformation() {
    const itemInfo = document.querySelector(".item-information");
    if (!itemInfo) return;
    itemInfo.remove();
}


function selectItem(item) {
    if (selectedItem !== item) {
        if (selectedItem) selectedItem.className = "item";

        item.className = "item selected";
        selectedItem = item;
        unrenderItemInformation();
        renderItemInformation(item);
    }
}


function unselectItem(e) {
    if (selectedItem && !selectedItem.contains(e.target)) {
        selectedItem.className = "item";
        selectedItem = null;
        unrenderItemInformation();
    }
}


async function openPropertiesWindow(itemType, item) {
    const propertiesWindow = document.createElement("div");
    switch (itemType) {
        case "grid":
            var folder = await getFolder(dataDiv.dataset.folderId);
            var folderPath = folder.path;
            var lastPathItemLength = folderPath.split("/").at(-1).length * -1;
            var parentFolder = folderPath.slice(0, lastPathItemLength);
            var filesMetadata = await getFolderTotalFiles(dataDiv.dataset.folderId);

            propertiesWindow.className = "properties-wrapper";
            propertiesWindow.innerHTML = `
            <div class="properties-window">
                <span class="folder-name">${folderPath.split("/").at(-1)}</span>
                <span class="folder-span-info">${filesMetadata[1]} item(s), totalling ${formatBytes(filesMetadata[0])}</span>
                <div class="folder-info">
                    <div class="folder-item">
                        <span class="folder-item-span">Parent Folder</span>
                        <span>${parentFolder}</span>
                    </div>
                    <div class="folder-item">
                        <span class="folder-item-span">Updated</span>
                        <span>${formatDate(folder.updated_at)}</span>
                    </div>
                    <div class="folder-item">
                        <span class="folder-item-span">Created</span>
                        <span>${formatDate(folder.created_at)}</span>
                    </div>
                </div>
            </div>
            `;
            propertiesWindow.addEventListener("click", async (e) => {
                if (propertiesWindow.querySelector(".properties-window").contains(e.target)) return;

                propertiesWindow.remove();
            });
            document.body.appendChild(propertiesWindow);
            break;

        case "folder":
            var folder = await getFolder(contextItem.dataset.id);
            var folderPath = folder.path;
            var lastPathItemLength = folderPath.split("/").at(-1).length * -1;
            var parentFolder = folderPath.slice(0, lastPathItemLength);
            var filesMetadata = await getFolderTotalFiles(contextItem.dataset.id);

            propertiesWindow.className = "properties-wrapper";
            propertiesWindow.innerHTML = `
            <div class="properties-window">
                <span class="folder-name">${folderPath.split("/").at(-1)}</span>
                <span class="folder-span-info">${filesMetadata[1]} item(s), totalling ${formatBytes(filesMetadata[0])}</span>
                <div class="folder-info">
                    <div class="folder-item">
                        <span class="folder-item-span">Parent Folder</span>
                        <span>${parentFolder}</span>
                    </div>
                    <div class="folder-item">
                        <span class="folder-item-span">Updated</span>
                        <span>${formatDate(folder.updated_at)}</span>
                    </div>
                    <div class="folder-item">
                        <span class="folder-item-span">Created</span>
                        <span>${formatDate(folder.created_at)}</span>
                    </div>
                </div>
            </div>
            `;
            propertiesWindow.addEventListener("click", async (e) => {
                if (propertiesWindow.querySelector(".properties-window").contains(e.target)) return;

                propertiesWindow.remove();
            });
            document.body.appendChild(propertiesWindow);
            break;

        case "file":
            var file = await getFileMetadata(contextItem.dataset.id);
            propertiesWindow.className = "properties-wrapper";
            propertiesWindow.innerHTML = `
            <div class="properties-window">
                <span class="folder-name">${file.filename}</span>
                <span class="folder-span-info">${formatBytes(file.size)}</span>
                <div class="folder-info">
                    <div class="folder-item">
                        <span class="folder-item-span">Parent Folder</span>
                        <span>${dataDiv.dataset.folderPath + "/"}</span>
                    </div>
                    <div class="folder-item">
                        <span class="folder-item-span">Updated</span>
                        <span>${formatDate(file.updated_at)}</span>
                    </div>
                    <div class="folder-item">
                        <span class="folder-item-span">Created</span>
                        <span>${formatDate(file.created_at)}</span>
                    </div>
                </div>
            </div>
            `;
            propertiesWindow.addEventListener("click", async (e) => {
                if (propertiesWindow.querySelector(".properties-window").contains(e.target)) return;

                propertiesWindow.remove();
            });
            document.body.appendChild(propertiesWindow);
            break;
    }
}


function closeContextMenus() {
    if (gridContextMenu.style.display === "block" || foldersContextMenu.style.display === "block" || filesContextMenu.style.display === "block") {
        gridContextMenu.style.display = "none";
        foldersContextMenu.style.display = "none";
        filesContextMenu.style.display = "none";
    }
}


function openContextMenu(type, event, item) {
    event.preventDefault();
    closeContextMenus();

    switch (type) {
        case "grid":
            gridContextMenu.style.top = `${event.clientY}px`;
            gridContextMenu.style.left = `${event.clientX}px`;
            gridContextMenu.style.display = 'block';
            break;

        case "folder":
            event.stopPropagation();
            if (item.querySelector("span").textContent === "..") return;

            selectItem(item);

            contextItem = item;

            foldersContextMenu.style.display = "block";
            foldersContextMenu.style.top = `${event.clientY}px`;
            foldersContextMenu.style.left = `${event.clientX}px`;
            break;

        case "file":
            event.stopPropagation();
            selectItem(item);

            filesContextMenu.dataset.id = item.dataset.id;
            filesContextMenu.dataset.type = item.dataset.mimeType;
            contextItem = item;

            filesContextMenu.style.display = "block";
            filesContextMenu.style.top = `${event.clientY}px`;
            filesContextMenu.style.left = `${event.clientX}px`;

            break;
    }
}


function openDialogWindow(purpose) {
    let dialogSpanText;
    let yesButtonText;
    let inputValue = "";

    switch (purpose) {
        case "create-folder":
            dialogSpanText = "New folder";
            yesButtonText = "Create";
            break;

        case "rename-folder":
            dialogSpanText = "Rename folder";
            yesButtonText = "Rename";
            inputValue = contextItem.querySelector("span").textContent;
            break;

        case "rename-file":
            dialogSpanText = "Rename file";
            yesButtonText = "Rename";
            inputValue = contextItem.querySelector("span").textContent;
            break;

        case "move-file":
            dialogSpanText = "Move file";
            yesButtonText = "Move";
            inputValue = dataDiv.dataset.folderPath;
            break;
    }

    dialogWindow.dataset.purpose = purpose;
    dialogWindow.innerHTML = `
    <span class="dialog-span">${dialogSpanText}</span>
    <input type="text" class="dialog-input" value="${inputValue}">
    <div class="dialog-buttons">
        <button data-action="no" class="dialog no">Cancel</button>
        <button data-action="yes" class="dialog yes">${yesButtonText}</button>
    </div>
    `;
    dialogWrapper.style.display = "flex";
}


dialogWindow.addEventListener("click", async (e) => {
    const action = e.target.dataset.action;

    switch (action) {
        case "no":
            dialogWrapper.style.display = "none";
            dialogWindow.innerHTML = "";
            break;

        case "yes":
            const purpose = dialogWindow.dataset.purpose;
            const dataFolderId = document.querySelector(".data-div").dataset.folderId;

            switch (purpose) {
                case "create-folder":
                    var inputValue = dialogWindow.querySelector("input").value.trim();
                    if (inputValue.length === 0) return;
                    if (inputValue === "..") return;

                    var response = await createFolder(dataFolderId, inputValue);
                    if (response.status !== 200) return alert("Error");

                    var folderId = await response.json();

                    var folder = document.createElement("div");
                    folder.className = "item folder";
                    folder.dataset.id = folderId;
                    folder.dataset.itemType = "folder";
                    folder.innerHTML = `
                    ${folderSVG}
                    <span>${inputValue}</span>
                    `;
                    try {
                        document.querySelector(".folders-grid").appendChild(folder);
                    } catch (error) {
                        var foldersGrid = document.createElement("div");
                        foldersGrid.className = "folders-grid";
                        foldersGrid.appendChild(folder);
                        gridContainer.prepend(foldersGrid);
                    }
                    addEventListenersToFolders(folder);

                    dialogWrapper.style.display = "none";
                    dialogWindow.innerHTML = "";
                    break;

                case "rename-folder":
                    var inputValue = dialogWindow.querySelector("input").value.trim();
                    if (inputValue.length === 0) return;
                    if (inputValue === "..") return;

                    var folderStatus = await updateFolder(contextItem.dataset.id, inputValue);
                    if (folderStatus !== 200) return alert("Error");

                    contextItem.querySelector("span").textContent = inputValue;

                    break;

                case "rename-file":
                    var inputValue = dialogWindow.querySelector("input").value.trim();
                    if (inputValue.length === 0) return;

                    var fileStatus = await updateFilename(contextItem.dataset.id, inputValue);
                    if (fileStatus !== 200) return alert("Error");

                    contextItem.querySelector("span").textContent = inputValue;

                    break;

                case "move-file":
                    var inputValue = dialogWindow.querySelector("input").value.trim();
                    if (inputValue.length === 0) return;
                    if (inputValue.at(-1) === "/") {
                        inputValue = inputValue.slice(0, -1);
                    }
                    if (inputValue === dataDiv.dataset.folderPath) return;

                    var folderResponse = await searchFolder(inputValue);
                    if (folderResponse.status !== 200) return alert("This folder doesn't exist");

                    var folder = await folderResponse.json();
                    var response = await updateFileLocation(contextItem.dataset.id, folder.id);
                    if (response.status !== 200) return alert("Error");

                    location.reload();

                    break;

            }
            dialogWrapper.style.display = "none";
            dialogWindow.innerHTML = "";
    }
});


gridContextMenu.addEventListener("click", async (e) => {
    const action = e.target.dataset.action;

    switch (action) {
        case "create-folder":
            openDialogWindow("create-folder");
            break;

        case "properties":
            openPropertiesWindow("grid", null);
            break;
    }
});


function openFolder(folder) {
    const folderId = folder.dataset.id;
    if (folderId === "home") return window.location.href = "/home";
    window.location.href = `/folders/${folderId}`;
}


async function addEventListenersToFolders(folder) {
    folder.addEventListener("click", async (e) => {
        selectItem(folder);
    });

    folder.addEventListener("contextmenu", async (e) => {
        openContextMenu("folder", e, folder);
    });

    folder.addEventListener("dblclick", async (e) => {
        openFolder(folder);
    });
}


folders.forEach(async (folder) => {
    addEventListenersToFolders(folder);
});


foldersContextMenu.addEventListener("click", async (e) => {
    const action = e.target.dataset.action;

    switch (action) {
        case "download":
            window.open(`/api/folders/${contextItem.dataset.id}/download`, "_blank");
            break;

        case "favorites":
            var response = await createFavorite(contextItem.dataset.id);
            if (response.status !== 200) return alert("Error");

            var favoritesWrapper = document.querySelector(".favorites-buttons-wrapper");
            var favoriteButton = document.createElement("button");
            favoriteButton.className = "fav-button";
            favoriteButton.dataset.id = contextItem.dataset.id;
            favoriteButton.addEventListener("click", (e) => {
                pressFavoriteButton(e);
            });
            favoriteButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px">
                <path d="M166.78-140.78q-44.3 0-75.15-30.85-30.85-30.85-30.85-75.15v-466.44q0-44.3 30.85-75.15 30.85-30.85 75.15-30.85h224.74L480-730.74h313.22q44.3 0 75.15 30.85 30.85 30.85 30.85 75.15v377.96q0 44.3-30.85 75.15-30.85 30.85-75.15 30.85H166.78Z"/>
            </svg>
            <span>${contextItem.querySelector("span").textContent}</span>
            <div class="fav-delete" onclick="pressDeleteFavoriteButton(event)">
                <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#ffffff">
                    <path d="M273.78-100.78q-44.3 0-75.15-30.85-30.85-30.85-30.85-75.15v-507q-22.09 0-37.54-15.46-15.46-15.46-15.46-37.54 0-22.09 15.46-37.55 15.45-15.45 37.54-15.45H347q0-22.09 15.46-37.55 15.45-15.45 37.54-15.45h158.87q22.09 0 37.54 15.45 15.46 15.46 15.46 37.55h180.35q22.09 0 37.54 15.45 15.46 15.46 15.46 37.55 0 22.08-15.46 37.54-15.45 15.46-37.54 15.46v507q0 44.3-30.85 75.15-30.85 30.85-75.15 30.85H273.78Zm155.57-193.26q13.48-13.48 13.48-32.74v-267.57q0-19.26-13.48-32.74t-32.74-13.48q-19.26 0-33.02 13.48-13.76 13.48-13.76 32.74v267.57q0 19.26 13.76 32.74 13.76 13.47 33.02 13.47 19.26 0 32.74-13.47Zm167.35 0q13.47-13.48 13.47-32.74v-267.57q0-19.26-13.47-32.74-13.48-13.48-32.74-13.48t-33.03 13.48q-13.76 13.48-13.76 32.74v267.57q0 19.26 13.76 32.74 13.77 13.47 33.03 13.47t32.74-13.47Z"/>
                </svg>
            </div>
            `;
            favoritesWrapper.appendChild(favoriteButton);

            break;

        case "rename":
            openDialogWindow("rename-folder");
            break;

        case "delete":
            const status = await deleteFolder(contextItem.dataset.id);
            if (status === 200) {
                contextItem.remove();
                var foldersGrid = document.querySelector(".folders-grid");
                if (foldersGrid) {
                    const items = foldersGrid.querySelectorAll(".item").length;
                    if (items === 0) {
                        foldersGrid.remove();
                    }
                }
                unrenderItemInformation();
            } else {
                alert("Error");
            }
            break;

        case "properties":
            openPropertiesWindow("folder", contextItem);
            break;
    }
});


async function openFile(file) {
    const fileId = file.dataset.id;
    const fileType = file.dataset.mimeType;

    const fileSource = `/api/files/${fileId}`;
    const fileGroup = fileType.split("/")[0];

    backgroundWrapper.style.display = "flex";

    let element;

    switch (fileGroup) {
        case "image":
            element = document.createElement("img");
            element.className = "background-div";
            element.src = fileSource;
            break;

        case "video":
            element = document.createElement("video");
            element.className = "background-div";
            element.controls = true;
            element.autoplay = true;
            element.src = fileSource;
            break;

        case "audio":
            element = document.createElement("audio");
            element.className = "background-div";
            element.controls = true;
            element.src = fileSource;
            element.file = fileType;
            break;

        case "text":
            element = document.createElement("div");
            element.className = "background-div text-container";
            var span = document.createElement("span");
            var content = await getFile(fileId);
            span.innerText = content;
            element.appendChild(span);
            break;

        default:
            element = document.createElement("div");
            element.className = "background-div";
            element.textContent = "Unsupported file type";
            break;
    }

    backgroundContainer.appendChild(element);
}


files.forEach(async (file) => {
    file.addEventListener("click", async (e) => {
        selectItem(file);
    });

    file.addEventListener("contextmenu", async (e) => {
        openContextMenu("file", e, file);
    });

    file.addEventListener("dblclick", async (e) => {
        openFile(file);
    });
});


filesContextMenu.addEventListener("click", async (e) => {
    const action = e.target.dataset.action;

    switch (action) {
        case "download":
            window.location.href = `/api/files/${filesContextMenu.dataset.id}/download`;
            break;

        case "move":
            openDialogWindow("move-file");
            break;

        case "rename":
            openDialogWindow("rename-file");
            break;

        case "delete":
            var status = await deleteFile(filesContextMenu.dataset.id);
            if (status === 200) {
                contextItem.remove();
                unrenderItemInformation();
            } else {
                alert("Error");
            }
            break;

        case "properties":
            openPropertiesWindow("file", contextItem);
            break;
    }
});


async function uploadFiles(files) {
    const uploadInformation = document.createElement("div");
    uploadInformation.className = "upload-information";
    uploadInformation.innerHTML = `
    <span>Uploading...</span>
    <span id="progress"></span>
    `;
    gridContainer.appendChild(uploadInformation);

    const formData = new FormData();
    for (let file of files) {
        formData.append("files", file);
    }

    const response = await uploadFile(document.querySelector(".data-div").dataset.folderId, formData);
}


fileInput.addEventListener("change", async (e) => {
    const files = e.target.files;

    await uploadFiles(files);
});


backgroundWrapper.addEventListener("click", async (e) => {
    if (!document.querySelector(".background-div").contains(e.target)) {
        backgroundWrapper.style.display = "none";
        backgroundContainer.innerHTML = "";
    }
});

document.getElementById("dropZone").addEventListener("dragover", async (e) => {
    e.preventDefault();
    e.stopPropagation();
});

document.getElementById("dropZone").addEventListener("drop", async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const files = e.dataTransfer.files;
    if (!files.length) return;

    await uploadFiles(files);
});
