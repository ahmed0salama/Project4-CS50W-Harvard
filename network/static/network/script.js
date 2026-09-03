function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
        
function editPost(postId) {
    const contentP = document.getElementById(`post-content-${postId}`);
    const editContainer = document.getElementById(`post-edit-container-${postId}`);
    const textarea = document.getElementById(`post-edit-textarea-${postId}`);
    const editBtn = document.getElementById(`edit-btn-${postId}`);

    textarea.value = contentP.innerText;

    contentP.style.display = 'none';
    editContainer.style.display = 'block';
    if (editBtn) editBtn.style.display = 'none';
}
        
function cancelEdit(postId) {
    const contentP = document.getElementById(`post-content-${postId}`);
    const editContainer = document.getElementById(`post-edit-container-${postId}`);
    const editBtn = document.getElementById(`edit-btn-${postId}`);

    contentP.style.display = 'block';
    editContainer.style.display = 'none';
    if (editBtn) editBtn.style.display = 'inline-block';
}
        
function savePost(postId) {
    const newContent = document.getElementById(`post-edit-textarea-${postId}`).value;

    fetch(`/edit/${postId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            content: newContent
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.message) {
            document.getElementById(`post-content-${postId}`).innerText = result.content;
            cancelEdit(postId);
        } else {
            alert(result.error || "Error updating post.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Failed to update post. Check console/URLs.");
    });
}

function toggleLike(postId) {
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        const likeBtn = document.getElementById(`like-btn-${postId}`);
        const likeCount = document.getElementById(`like-count-${postId}`);

        if (result.liked) {
            likeBtn.className = "btn btn-sm btn-danger mr-2";
            likeBtn.innerHTML = "❤️ Unlike";
        } else {
            likeBtn.className = "btn btn-sm btn-outline-danger mr-2";
            likeBtn.innerHTML = "🤍 Like";
        }

        likeCount.innerHTML = `<strong>${result.likes_count}</strong> Likes`;
    })
    .catch(error => {
        console.error('Error toggling like:', error);
    });
}