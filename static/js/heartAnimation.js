// parentNodeId: string. Example: "list-post"
// Option: string. Example: "like_post"
function animateHeart(parentNodeId, option) {
    document.getElementById(parentNodeId).addEventListener('click', function (event) {
        let target = event.target; // where was the click?
        if (target.tagName !== 'A') return; // not on TD? Then we're not interested

        let likeNumberElement = target.nextElementSibling;
        let likeNumber = parseInt(likeNumberElement.textContent);
        if (target.dataset.action === 'like') {
            target.setAttribute('hx-get', `{{ url_for('${option}') }}?id=${target.dataset.id}&action="unliked"`)
            likeNumberElement.innerHTML = (likeNumber + 1).toString()
            target.dataset.action = 'liked';
            target.classList.remove('fa-regular');
            target.classList.add('fa-solid');
            target.classList.add('fa-bounce');
            setTimeout(function () {
                target.classList.remove('fa-bounce');
            }, 1000);
        } else if (target.dataset.action === 'unliked') {
            target.setAttribute('hx-get', `{{ url_for('${option}') }}?id=${target.dataset.id}&action="like"`)
            likeNumberElement.innerHTML = (likeNumber - 1).toString()
            target.dataset.action = 'like';
            target.classList.remove('fa-solid');
            target.classList.add('fa-regular');
            target.classList.remove('fa-bounce');
        }
    });
}


