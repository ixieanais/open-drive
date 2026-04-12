async function uploadFile(folderId, formData) {
    const progress = document.getElementById("progress");
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `/api/folders/${folderId}/files`);

    xhr.onload = () => {
        if (xhr.status === 200) {
            const uploadInformation = document.querySelector(".upload-information");
            uploadInformation.style.opacity = "0";
            setTimeout(async () => {
                uploadInformation.remove();
                location.reload();
            }, 1000);
        }
    }

    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const percent = (event.loaded / event.total) * 100;
            progress.textContent = percent.toFixed(2) + "%";
        }
    };

    xhr.send(formData)

    return xhr.status;
}

// async function getFiles(folderId) {
//     const response = await fetch(`/api/folders/${folderId}/files`, {
//         method: "GET",
//         headers: {
//             "Content-Type": "application/json"
//         }
//     });
//     return await response.json();
// }


async function searchFiles(query) {
    const url = "/api/files/search?" + new URLSearchParams({query: query}).toString()
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        },
    });
    return await response.json();
}

async function getFile(fileId) {
    const response = await fetch(`/api/files/${fileId}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.text();
}

async function getFileMetadata(fileId) {
    const response = await fetch(`/api/files/${fileId}/meta`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}

async function updateFilename(fileId, name) {
    const response = await fetch(`/api/files/${fileId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({name: name})
    });
    return response.status;
}

async function updateFileLocation(fileId, folderId) {
    const response = await fetch(`/api/files/${fileId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({folder_id: folderId})
    });

    return response;
}

async function deleteFile(fileId) {
    const response = await fetch(`/api/files/${fileId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return response.status;
}



async function createFolder(parentId, name) {
    const response = await fetch(`/api/folders/${parentId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({name: name})
    });
    return response;
}

async function getFolders(parentId) {
    const response = await fetch(`/api/folders/${parentId}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}

async function getFolder(folderId) {
    const response = await fetch(`/api/folders/${folderId}/metadata`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}

async function getFolderTotalFiles(folderId) {
    const response = await fetch(`/api/folders/${folderId}/files/total`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json()
}

async function searchFolder(path) {
    const url = "/api/folders/search?" + new URLSearchParams({path: path}).toString()
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return response;
}

async function searchFolders(query) {
    const url = "/api/folders/search?" + new URLSearchParams({query: query}).toString()
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}

async function getMainFolder() {
    const response = await fetch(`/api/folders/main`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return await response.json();
}

async function updateFolder(folderId, name) {
    const response = await fetch(`/api/folders/${folderId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({name: name})
    });
    return response.status;
}

async function deleteFolder(folderId) {
    const response = await fetch(`/api/folders/${folderId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    });
    return response.status;
}



async function createFavorite(folderId) {
    const response = await fetch(`/api/favorites/${folderId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    });

    return response;
}

async function deleteFavorite(folderId) {
    const response = await fetch(`/api/favorites/${folderId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    });

    return response;
}
