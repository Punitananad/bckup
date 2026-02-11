function NotifyUser() {
    const audio = new Audio("/static/sound/notification.wav");
    for (let i = 0; i < 10; i++) {
        try {
            audio.play();
            break;
        }
        catch (error) {
            continue;
        }
    }
}

function NotifyIncomingMessage() {
    const audio = new Audio("/static/sound/msg_recived_from_custmer.mp3")
    for (let i = 0; i < 10; i++) {
        try {
            audio.play();
            break;
        }
        catch (error) {
            continue;
        }
    }
}

// LAST MESSAGE
var LastMessage;

// GET THE CSRF TOKEN
const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

// VAR CUSTOMER PHONE NUMBER
var PhoneNumber

// USER ID
const UserId = JSON.parse(document.getElementById('current-user').innerText);

// BUTTON SHOW THE NUMBER OF UNSEEN MESSAGES AND SHOW THE ALL CHAT USERS
const chatButton = document.getElementById('chat-button');


// AREA WHERE WE ARE ABLE TO SEE ALL THE USERS / CHAT USERS
const allUserArea = document.getElementById('all-chat-users');

// AREA FOR MESSAGING
const chatArea = document.getElementById('chat-box');

// CHAT HEADER
const SeatNameLabel = document.getElementById('chat-seat-label');
const PhoneNumberLabel = document.getElementById('chat-phone-label');

const chatWorker = new Worker('/static/theatre_js/chat-box/worker.js?v=' + Date.now())

chatButton.addEventListener('click', () => {
    const task = {
        task: 'load-all-users'
    }
    chatWorker.postMessage(task);
})

// SAVE THE THEATRE ID
chatWorker.postMessage(
    {
        task: 'save-theatre-id',
        theatre_id: theatre_id,
        csrf_token: csrftoken,
    }
)

var chat_socket_url

if (window.location.href.includes('https')) {
    chat_socket_url = `wss://${window.location.host}/ws/chat-socket/`
}
else {
    chat_socket_url = `ws://${window.location.host}/ws/chat-socket/`
}

// CHAT FORM TO SEND THE MESSAGE TO THE WHATSAPP USER FROM THE LIVE ORDER PAGE.
const ChatForm = document.getElementById('chat-form');

// ADD EVENT LISTENER ON TIME OF SUBMIT OR SEND BUTTON.
ChatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const messageInput = document.getElementById('user-input');

    const task = {
        task: 'send-message-to-whatsapp',
        current_user_id: UserId,
        message: messageInput.value,
        phone_number: PhoneNumber,
    }

    if (messageInput.value.replaceAll(' ', '') === "") {
        messageInput.setAttribute('class', 'form-control is-invalid')
    }

    else {
        chatWorker.postMessage(task);
        messageInput.setAttribute('class', 'form-control')
        messageInput.value = "";
    }

})

// FUNCTION CALCULATE MSG COMOE HOW MUCH TIME AGO
function timeAgo(timeString) {
    // Parse given string to Date
    const parsedDate = new Date(Date.parse(timeString.replace(/-/g, " ")));

    if (isNaN(parsedDate)) {
        return "Invalid date";
    }

    const now = new Date();
    const diffMs = now - parsedDate; // Difference in ms
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);
    const diffMonth = Math.floor(diffDay / 30);
    const diffYear = Math.floor(diffDay / 365);

    if (diffSec < 60) {
        return `${diffSec} sec ago`;
    } else if (diffMin < 60) {
        return `${diffMin} min ago`;
    } else if (diffHr < 24) {
        return `${diffHr} hour${diffHr > 1 ? "s" : ""} ago`;
    } else if (diffDay < 30) {
        return `${diffDay} day${diffDay > 1 ? "s" : ""} ago`;
    } else if (diffMonth < 12) {
        return `${diffMonth} month${diffMonth > 1 ? "s" : ""} ago`;
    } else {
        return `${diffYear} year${diffYear > 1 ? "s" : ""} ago`;
    }
}

// FUNCTION TO LOAD ALL USERS
function loadUsers(all_users) {

    // GET USER MESSAGES
    function GetMessages(phone_number) {
        chatArea.innerHTML = "";
        const task = {
            'task': 'get-user-messages',
            'phone_key': `phone-${phone_number}`
        }
        chatWorker.postMessage(task);
    }

    'THIS CODE IS TO LOAD ALL THE USERS IN THE LI'
    const chatUserDiv = document.getElementById('all-chat-users')
    chatUserDiv.innerHTML = ""

    for (let user in all_users) {

        const user_data = all_users[user]
        const user_theatre_id = user_data.theatre_id;
        if (user_theatre_id === theatre_id) {
            const li = document.createElement('li');
            li.setAttribute('class', 'list-group-item contact');

            var span_html = ""
            if (user_data.reply_required) {
                span_html = '<span class="badge bg-danger chat-badge">...</span>'
            }

            li.innerHTML = `
            <div>
                <div>
                    ${user_data.hall_name}, ${user_data.seat_name}
                    ${span_html}
                </div>
                <div class="text-end">
                    <span class="text-muted small float-end">
                        ${timeAgo(user_data.msg_time)}
                    </span>
                </div>
            </div>
            `
            li.addEventListener('click', () => {
                GetMessages(user_data.phone_number)
            })
            chatUserDiv.appendChild(li);
        }
    }
}

// FUNCTION UPDATE CHAT COUNT
function UpdateChatButtonCount(chat_count) {
    chatButton.innerHTML = `
        All Chats
        <span class="badge bg-danger">
            ${chat_count}
        </span>
    `
}

// FUNCTION TO START THE WEBSOCKET
function startChatSocket(socket_url) {
    const task = {
        task: 'start-websocket',
        socket_url: socket_url
    }
    chatWorker.postMessage(task);
}

function AddSingleMessage(message, new_msg = false) {

    const msg = document.createElement('div');

    // WHETHER THE MESSAGE IS INCOMING OR OUTGOING
    const msg_typ = message.msg_type;
    let msg_html = ""

    if (msg_typ === 'INCOMING') {

        msg_html = `
                    <div class="message-row received">
                        <img src="https://img.freepik.com/premium-vector/person-with-blue-shirt-that-says-name-person_1029948-7040.jpg" class="message-avatar" alt="User">'
                        <div class="message-bubble">
                            ${message.context}
                            <div class="text-muted small text-start mt-1 tmg">
                                ${timeAgo(message.msg_time)}
                            </div>
                        </div>
                    </div>
        `
    }

    else if (msg_typ === "TEMPLATE") {
        // UPDATE THE SEAT NAME AND PHONE NUMBER
        msg_html = `
                    <div class="message-row sent">
                        <div class="message-bubble">
                            ${message.template}

                            <div class="text-muted end text-start mt-1 tmg">
                                ${timeAgo(message.msg_time)}
                            </div>
                        </div>
                        <img src="/static/assets/images/brand/favicon.png" class="message-avatar" alt="Me">
                    </div>
        `
    }

    else {
        msg_html = `
                    <div class="message-row sent">
                        <div class="message-bubble">
                            ${message.context}
                            <div class="text-muted end text-start mt-1 tmg">
                                ${timeAgo(message.msg_time)}
                            </div>
                        </div>
                        <img src="${message.img_url}" class="message-avatar" alt="Me">
                    </div>
        `
    }

    msg.innerHTML = msg_html;
    if (new_msg === true) {
        chatArea.append(msg);
    }
    else {
        chatArea.prepend(msg);
    }

    chatArea.scrollTop = chatArea.scrollHeight;
}



startChatSocket(chat_socket_url);

chatWorker.onmessage = (e) => {
    const eventData = e.data;
    const task_name = eventData.task;

    if (task_name === "update-chat-count") {
        const chat_count = eventData.chat_count;
        UpdateChatButtonCount(chat_count);
    }

    else if (task_name === "load-all-users") {
        const chat_users = eventData.chat_users;
        loadUsers(chat_users);
    }

    else if (task_name === 'load-chats') {
        const phone_number = eventData.phone_number;
        const messages = eventData.messages;

        PhoneNumber = phone_number;
        PhoneNumberLabel.innerText = PhoneNumber;

        SeatNameLabel.innerText = `${eventData.hall_name}, ${eventData.seat_name}`


        for (let i = 0; i < messages.length; i++) {
            const message = messages[i];
            AddSingleMessage(message);
            LastMessage = message.msg_type
        }
        $("#msg-card-box").modal('show')

    }

    else if (task_name === "update-new-message") {
        const message = eventData.message
        const phone_number = eventData.phone_number
        
        if (message.msg_type === 'INCOMING') {
            NotifyIncomingMessage()
        }
        else {
            NotifyUser()
        }

        if (PhoneNumber === phone_number) {
            AddSingleMessage(message, true)
        }
    }
}
