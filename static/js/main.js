const storageWrapper = document.querySelector(".storage-wrapper");
const gridWrapper = document.querySelector(".grid-wrapper");
const homeButton = document.getElementById("home-button");


function renderDiskUsage() {
    const diskUsage = JSON.parse(dataDiv.dataset.diskUsage);
    const diskUsagePercent = (diskUsage.used / diskUsage.total) * 100;

    document.querySelector(".disk-progress").style.width = diskUsagePercent + "%";

    const diskText = document.querySelector(".disk-text");
    diskText.textContent = `${formatBytes(diskUsage.used)} / ${formatBytes(diskUsage.total)} (${diskUsagePercent.toFixed(1)}%)`;
}


homeButton.addEventListener("click", () => window.location.href = "/home");


storageWrapper.addEventListener("click", async (e) => {
    unselectItem(e);
});


storageWrapper.addEventListener("contextmenu", async (e) => {
    unselectItem(e);
    openContextMenu("grid", e, null);
});


gridWrapper.addEventListener("scroll", async (e) => {
    closeContextMenus();
});


document.addEventListener("click", async (e) => {
    closeContextMenus();
});

renderDiskUsage();