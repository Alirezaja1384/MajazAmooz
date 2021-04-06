let tutorialId = parseInt(document.querySelector("#TutorialId").value)


let AllowReplies=document.getElementById("AllowReplies");
let NotifyReplies=document.getElementById("NotifyReplies");


AllowReplies.addEventListener('click',() => NotifyReplies.disabled = !(NotifyReplies.checked = AllowReplies.checked));



function ReplyTo(commentId,commentTitle)
{
    document.getElementById('Comment_Reply_To').value = commentId;
    document.getElementById('ReplyTo-Alert-CommentTitle').innerHTML = commentTitle;
    $("#ReplyTo-Alert").show();
    $("#CommentTitle").focus();
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
        "TutorialId": parseInt(document.getElementById('TutorialId').value),
        "CommentTitle": document.getElementById('CommentTitle').value,
        "CommentText": document.getElementById('CommentText').value,
        "AllowReplies": document.getElementById('AllowReplies').checked,
        "NotifyReplies": document.getElementById('NotifyReplies').checked,
        "Comment_Reply_To": replyTo !== 0 ? replyTo : null
    }
    fetch('/API/TutorialComment/InsertTutorialComment', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
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

    fetch('/API/Tutorial/InsertOrRemoveTutorialUpVote', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tutorialId)
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: 'خطایی سمت سرور اتفاق افتاد',
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

    fetch('/API/Tutorial/InsertOrRemoveTutorialDownVote', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tutorialId)
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: 'خطایی سمت سرور اتفاق افتاد',
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

    fetch('/API/Tutorial/InsertOrRemoveTutorialLike', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tutorialId)
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: 'خطایی سمت سرور اتفاق افتاد',
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

    fetch('/API/TutorialComment/InsertOrRemoveTutorialCommentUpVote', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'comment_id': tutorialCommentId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: 'خطایی سمت سرور اتفاق افتاد',
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

    fetch('/API/TutorialComment/InsertOrRemoveTutorialCommentDownVote', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'comment_id': tutorialCommentId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0)
                Swal.fire({
                    title: 'خطا',
                    text: 'خطایی سمت سرور اتفاق افتاد',
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

    fetch('/API/TutorialComment/InsertOrRemoveTutorialCommentLike', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'comment_id': tutorialCommentId})
    }).then(response => response.json())
        .then(content => {
            if (parseInt(content["status"]) === 0) {
                Swal.fire({
                    title: 'خطا',
                    text: 'خطایی سمت سرور اتفاق افتاد',
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
