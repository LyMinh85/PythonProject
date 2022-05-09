// parentNodeId: string. Example: "list-post"
function animateHeart(parentNodeId) {
    document.getElementById(parentNodeId).addEventListener('click', function (event) {
        let target = event.target; // where was the click?
        if (target.tagName !== 'A') return; // not on TD? Then we're not interested
        if (target.dataset.action !== 'like' && target.dataset.action !== 'unliked') return;
        console.log(target);
        let likeNumberElement = target.nextElementSibling;
        let likeNumber = parseInt(likeNumberElement.textContent);
        if (target.dataset.action === 'like') {
            likeNumberElement.innerHTML = (likeNumber + 1).toString()
            target.dataset.action = 'unliked';
            target.classList.remove('fa-regular');
            target.classList.add('fa-solid');
            target.classList.add('fa-bounce');
            setTimeout(function () {
                target.classList.remove('fa-bounce');
            }, 1000);
        } else if (target.dataset.action === 'unliked') {
            likeNumberElement.innerHTML = (likeNumber - 1).toString()
            target.dataset.action = 'like';
            target.classList.remove('fa-solid');
            target.classList.add('fa-regular');
            target.classList.remove('fa-bounce');
        }
    });
}

// parentNodeId: string. Example: "list-post"
function copyLinkToClipBoard(parentNodeId) {
    document.getElementById(parentNodeId).addEventListener('click', function (event) {
        let target = event.target; // where was the click?
        if (target.tagName !== 'A') return;
        if (target.dataset.action !== 'copy-link') return;
        let linkText =  `${window.location.href}${target.dataset.link}`;
        navigator.clipboard.writeText(linkText).then(function () {
            console.log('Async: Copying to clipboard was successful!');
        }, function (err) {
            console.error('Async: Could not copy text: ', err);
        });
    })
}

