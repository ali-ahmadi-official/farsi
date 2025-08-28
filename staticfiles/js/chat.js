const scrollingBox = document.getElementById('chat-content');
scrollingBox.scrollTop = scrollingBox.scrollHeight;

// const observer = new MutationObserver(() => {
//     scrollingBox.scrollTop = scrollingBox.scrollHeight;
// });

// observer.observe(scrollingBox, { childList: true });

// function getCookie(name) {
//     var cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         var cookies = document.cookie.split(';');
//         for (var i = 0; i < cookies.length; i++) {
//             var cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }

// const csrftoken = getCookie('csrftoken');

// function fetchMessages() {
//     const lastMessageId = $('#chat-content .media-chat').last().attr('id') || 0;
//     var currentUrl = window.location.href;
//     var urlParts = currentUrl.split('/');
//     var chatId = urlParts[urlParts.length - 2];
//     var requestUrl = `http://localhost:8000/chats/${chatId}/update/?after_id=${lastMessageId}`;

//     $.ajax({
//         url: requestUrl,
//         type: 'GET',
//         headers: { 'X-CSRFToken': csrftoken },
//         success: function (data) {
//             $('#chat-content').append(data);
//         }
//     });
// }

// $(document).ready(function () {
//     setInterval(fetchMessages, 5000);
// });

document.getElementById('file-input').addEventListener('change', function () {
    var file = this.files[0];
    var maxSize = 25 * 1024 * 1024;

    if (file.size > maxSize) {
        alert('حجم فایل بیش از 25 مگابایت است!');
        this.value = '';
        document.getElementById('fileNameBox').innerText = '';
    } else {
        var fileName = file.name;
        document.getElementById('fileNameBox').innerText = 'فایل شما: ' + fileName;
    }
});

const down = document.getElementById('down');
const threshold = 80;

function checkScrollability() {
    if (scrollingBox.scrollHeight <= scrollingBox.clientHeight) {
        down.classList.add('hidden');
    } else {
        if (scrollingBox.scrollTop + scrollingBox.clientHeight >= scrollingBox.scrollHeight - threshold) {
            down.classList.add('hidden');
        } else {
            down.classList.remove('hidden');
        }
    }
}

scrollingBox.addEventListener('scroll', checkScrollability);

down.addEventListener('click', () => {
    scrollingBox.scrollTo({
        top: scrollingBox.scrollHeight,
        behavior: 'smooth'
    });
});

window.addEventListener('load', checkScrollability);

const black = document.querySelector('.black');
function showInfo(button) {
    const parent1 = button.parentElement;
    const parent2 = parent1.parentElement;
    const parent3 = parent2.parentElement;
    const x = parent3.querySelector('#x');    
    const id = parent3.id;

    const infoId = `info_${id}`;
    const infoDiv = document.getElementById(infoId);
    
    if (infoDiv) {
        infoDiv.style.display = 'block';
        black.style.display = 'block';
    }

    x.addEventListener('click', () => {
        infoDiv.style.display = 'none';
        black.style.display = 'none';
    });
}
