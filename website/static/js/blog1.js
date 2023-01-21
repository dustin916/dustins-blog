function deleteSubscribers(subscribersId) {
    fetch('/delete-subscribers', {
        method: 'POST',
        body: JSON.stringify({ subscribersId: subscribersId })
    }).then((_res) => {
        window.location.href = "/dash-subscribers";
    });
}

function deleteBlog(blogId) {
    fetch('/delete-blog', {
        method: 'POST',
        body: JSON.stringify({ blogId: blogId })
    }).then((_res) => {
        window.location.href = "/dash-blog";
    });
}

function deleteAbout(aboutId) {
    fetch('/delete-about', {
        method: 'POST',
        body: JSON.stringify({ aboutId: aboutId })
    }).then((_res) => {
        window.location.href = "/dash-about-me";
    });
}

function deleteProfPic(profpicId) {
    fetch('/delete-profpic', {
        method: 'POST',
        body: JSON.stringify({ profpicId: profpicId })
    }).then((_res) => {
        window.location.href = "/dash-about-me";
    });
}

function deleteImages(imagesId) {
    fetch('/delete-images', {
        method: 'POST',
        body: JSON.stringify({ imagesId: imagesId })
    }).then((_res) => {
        window.location.href = "/dash-images";
    });
}

function deleteSermon(sermonsId) {
    fetch('/delete-sermon', {
        method: 'POST',
        body: JSON.stringify({ sermonsId: sermonsId })
    }).then((_res) => {
        window.location.href = "/dash-sermons";
    });
}
