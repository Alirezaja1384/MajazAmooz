const TutorialId = parseInt(document.querySelector("#TutorialId").value)
const csrftoken = Cookies.get('csrftoken');

let AllowReplies=document.getElementById("AllowReplies");
let NotifyReplies=document.getElementById("NotifyReplies");


AllowReplies.addEventListener('click',() => NotifyReplies.disabled = !(NotifyReplies.checked = AllowReplies.checked));



function ReplyTo(commentId,comment_title)
{
    document.getElementById('Comment_Reply_To').value = commentId;
    document.getElementById('ReplyTo-Alert-comment_title').innerHTML = comment_title;
    $("#ReplyTo-Alert").show();
    $("#comment_title").focus();
}


document.getElementById('Close-ReplyTo-Alert').addEventListener('click',()=>{
    let commentReplyTo = document.getElementById('Comment_Reply_To');
    commentReplyTo.value="";
    $("#ReplyTo-Alert").hide();
});



document.getElementById('TutorialSubmitCommentForm').addEventListener('submit',function(e) {

    e.preventDefault();

    let replyTo = parseInt(document.getElementById('Comment_Reply_To').value);

    let data = {
        "tutorial": parseInt(document.getElementById('TutorialId').value),
        "title": document.getElementById('CommentTitle').value,
        "text": document.getElementById('CommentText').value,
        "allow_reply": document.getElementById('AllowReplies').checked,
        "notify_replies": document.getElementById('NotifyReplies').checked,
        "reply_to": replyTo !== 0 ? replyTo : null
    }
    fetch('/ajax/create_tutorial_comment', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    }).then(response => response.json())
        .then(content => {
                if (content["status"])
                    Swal.fire({
                        title: 'نظر شما با موفقیت ثبت شد',
                        text: 'نظر شما پس از تایید قابل مشاهده خواهد بود',
                        icon: 'success',
                        confirmButtonText: 'تایید',
                        timer: 5000
                    });
                else
                    Swal.fire({
                        title: 'خطا',
                        text: content["error"],
                        icon: 'error',
                        confirmButtonText: 'تایید'
                    });
                Swal.fire({
                    title: 'خطا',
                }).catch(() => {
                    Swal.fire({
                        text: 'ارتباط با سرور برقرار نشد',
                        icon: 'error',
                        confirmButtonText: 'تایید'
                    });
                });
            }
        );
})

let UpVoteTutorialBTN = document.getElementById('UpVoteTutorial');
UpVoteTutorialBTN.addEventListener('click', () => {

    UpVoteTutorialBTN.classList.add("disabled");

    fetch('/ajax/tutorial_upvote', {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'tutorial_id': TutorialId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: content["error"] ? content["error"] : 'خطایی سمت سرور اتفاق افتاد',
                    icon: 'error',
                    confirmButtonText: 'تایید'
                });
            else {
                let upVotes = document.getElementById("TutorialUpVotesCount");
                let nextUpVoteCount = parseInt(upVotes.innerHTML) + parseInt(content["status"]);
                upVotes.innerHTML = nextUpVoteCount.toString();

                UpVoteTutorialBTN.classList.remove("disabled");
            }
        }).catch(() => {
        Swal.fire({
            title: 'خطا',
            text: 'ارتباط با سرور برقرار نشد',
            icon: 'error',
            confirmButtonText: 'تایید'
        });
    });
});

let downVoteTutorial = document.getElementById('DownVoteTutorial')
downVoteTutorial.addEventListener('click', () => {

    downVoteTutorial.classList.add("disabled");

    fetch('/ajax/tutorial_downvote', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({"tutorial_id": TutorialId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: content["error"] ? content["error"] : 'خطایی سمت سرور اتفاق افتاد',
                    icon: 'error',
                    confirmButtonText: 'تایید'
                });
            else {
                let downVotes = document.getElementById("TutorialDownVotesCount");
                let nextDownVoteCount = parseInt(downVotes.innerHTML) + parseInt(content["status"]);
                downVotes.innerHTML = nextDownVoteCount.toString();

                downVoteTutorial.classList.remove("disabled");
            }
        }).catch(() => {
        Swal.fire({
            title: 'خطا',
            text: 'ارتباط با سرور برقرار نشد',
            icon: 'error',
            confirmButtonText: 'تایید'
        });
    });
});


let LikeBTN = document.getElementById('LikeTutorial');
LikeBTN.addEventListener('click', () => {
    
    LikeBTN.classList.add("disabled");

    fetch('/ajax/tutorial_like', {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'tutorial_id': TutorialId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: content["error"] ? content["error"] : 'خطایی سمت سرور اتفاق افتاد',
                    icon: 'error',
                    confirmButtonText: 'تایید'
                });
            else {
                switch (content["status"]) {
                    case(1):
                        LikeBTN.classList.remove("btn-outline-danger");
                        LikeBTN.classList.add("btn-danger");
                        break;
                    case(-1):
                        LikeBTN.classList.remove("btn-danger");
                        LikeBTN.classList.add("btn-outline-danger");
                        break;
                }
                let likes = document.getElementById("TutorialLikesCount");
                let nextLikesCount = parseInt(likes.innerHTML) + parseInt(content["status"]);
                likes.innerHTML = nextLikesCount.toString();

                LikeBTN.classList.remove("disabled");
            }
        }).catch(() => {
        Swal.fire({
            title: 'خطا',
            text: 'ارتباط با سرور برقرار نشد',
            icon: 'error',
            confirmButtonText: 'تایید'
        });
    });
});


function UpVoteTutorialComment(tutorialCommentId) {
    let commentUpVoteBTN = document.getElementById("comment-upvote-btn-" + tutorialCommentId);
    commentUpVoteBTN.classList.add("disabled");

    fetch('/ajax/tutorial_comment_upvote', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'comment_id': tutorialCommentId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: content["error"] ? content["error"] : 'خطایی سمت سرور اتفاق افتاد',
                    icon: 'error',
                    confirmButtonText: 'تایید'
                });
            else {
                let upVotes = document.getElementById("TutorialCommentUpVotesCount-" + tutorialCommentId);
                let nextUpVoteCount = parseInt(upVotes.innerHTML) + parseInt(content["status"]);
                upVotes.innerHTML = nextUpVoteCount.toString();

                commentUpVoteBTN.classList.remove("disabled");
            }
        }).catch(() => {
        Swal.fire({
            title: 'خطا',
            text: 'ارتباط با سرور برقرار نشد',
            icon: 'error',
            confirmButtonText: 'تایید'
        });
    });
}


function DownVoteTutorialComment(tutorialCommentId) {
    let commentDownVoteBTN = document.getElementById("comment-downvote-btn-" + tutorialCommentId);
    commentDownVoteBTN.classList.add("disabled");

    fetch('/ajax/tutorial_comment_downvote', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'comment_id': tutorialCommentId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: content["error"] ? content["error"] : 'خطایی سمت سرور اتفاق افتاد',
                    icon: 'error',
                    confirmButtonText: 'تایید'
                });
            else {
                let downVotes = document.getElementById("TutorialCommentDownVotesCount-" + tutorialCommentId);
                let nextDownVoteCount = parseInt(downVotes.innerHTML) + parseInt(content["status"]);
                downVotes.innerHTML = nextDownVoteCount.toString();

                commentDownVoteBTN.classList.remove("disabled");
            }
        }).catch(() => {
        Swal.fire({
            title: 'خطا',
            text: 'ارتباط با سرور برقرار نشد',
            icon: 'error',
            confirmButtonText: 'تایید'
        });
    });
}


function LikeTutorialComment(tutorialCommentId) {
    let commentLikeBTN = document.getElementById("comment-like-btn-" + tutorialCommentId);
    commentLikeBTN.classList.add("disabled");

    fetch('/ajax/tutorial_comment_like', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'comment_id': tutorialCommentId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0) {
                Swal.fire({
                    title: 'خطا',
                    text: content["error"] ? content["error"] : 'خطایی سمت سرور اتفاق افتاد',
                    icon: 'error',
                    confirmButtonText: 'تایید'
                });
            } else {
                let likes = document.getElementById("TutorialCommentLikesCount-" + tutorialCommentId);
                let nextLikeCount = parseInt(likes.innerHTML) + parseInt(content["status"]);
                likes.innerHTML = nextLikeCount.toString();

                commentLikeBTN.classList.remove("disabled");
            }
        }).catch(() => {
        Swal.fire({
            title: 'خطا',
            text: 'ارتباط با سرور برقرار نشد',
            icon: 'error',
            confirmButtonText: 'تایید'
        });
    });
}

