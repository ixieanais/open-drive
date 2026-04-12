function pressFavoriteButton(event) {
    const button = event.target.closest("button");
    const folderId = button.dataset.id;
    location.href = `/folders/${folderId}`;
}

async function pressDeleteFavoriteButton(event) {
    event.stopPropagation();
    const button = event.target.closest("button");
    const folderId = button.dataset.id;
    const response = await deleteFavorite(folderId);
    if (response.status !== 200) return alert("Error");

    button.remove();
}