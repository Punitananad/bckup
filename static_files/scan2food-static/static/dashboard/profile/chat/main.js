const worker = new Worker('/static/dashboard/profile/chat/worker.js?v=' + Date.now())
const order_id = parseInt(JSON.parse(document.head.getElementsByTagName('title')[0].innerText.split("|")[1]));

var CHAT_SOCKET_URL;

var CHAT_SOCKET;

if (window.location.href.includes('https')) {
    CHAT_SOCKET_URL = `wss://${window.location.host}/ws/chat-socket/`
}
else {
    CHAT_SOCKET_URL = `ws://${window.location.host}/ws/chat-socket/`
}

function LoadUpCSRFToken() {
    const csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    const task = {
        name: 'load-csrf-token',
        csrf_token: csrf_token
    }
    worker.postMessage(task);
}

LoadUpCSRFToken();

function clearChatArea() {
    document.getElementById('chat-area').innerHTML = "";
}

function LoadAllChats() {
    const taks = {
        name: 'load-all-chats',
        orderId: order_id
    }
    worker.postMessage(taks);
}

function scrollToBottom() {
    const chatArea = document.getElementById('chat-area');
    chatArea.scrollTop = chatArea.scrollHeight;
}

function LoadSingleMessage(data, new_msg) {

    const chatArea = document.getElementById('chat-area')

    const msg_type = data.msg_type;
    const formated = data.msg_time;

    const msg = document.createElement('div');
    switch (msg_type) {
        case ('TEMPLATE'):
            let order_url = ''
            if (data.order_id !== order_id) {
                order_url = `
                <div>
                    <a href="/admin-portal/order-profile/${data.order_id}" target="_blank" class="badge badge-success bg-success">
                        <i class="fa fa-share" aria-hidden="true"></i>
                        Open Order
                    </a>
                </div>
                `
            }
            msg.innerHTML = `
                <div class="message-row sent">
                    <div class="message-bubble">
                        ${data.template}
                        ${order_url}
                        <div class="text-muted end text-start mt-1 tmg">
                            ${formated}
                        </div>
                    </div>
                    <img src="/static/assets/images/brand/favicon.png" class="message-avatar" alt="Me">
                </div>
                `
            break;

        case ('OUTGOING'):
            msg.innerHTML = `
                <div class="message-row sent">
                    <div class="message-bubble">
                        ${data.context}
                        <div class="text-muted end text-start mt-1 tmg">
                            ${formated}
                        </div>
                    </div>
                    <img src="${data.img_url}" class="message-avatar" alt="Me">
                </div>
            `
            break;

        case ('INCOMING'):
            msg.innerHTML = `
                <div class="message-row received">
                    <img src="https://img.freepik.com/premium-vector/person-with-blue-shirt-that-says-name-person_1029948-7040.jpg"
                        class="message-avatar" alt="User">'
                    <div class="message-bubble">
                        ${data.context}
                        <div class="text-muted small text-start mt-1 tmg">
                            ${formated}
                        </div>
                    </div>
                </div>
            `

    }

    if (new_msg) {
        chatArea.append(msg)
    }
    else {
        chatArea.insertAdjacentElement("beforeend", msg);
    }
    scrollToBottom()
}

// CATCH MESSAGE FROM THE WORKER
worker.onmessage = (event) => {
    const task = event.data;
    const task_name = task.name;

    if (task_name === 'load-single-chat') {
        const data = task.data;
        const new_msg = task.new_msg
        LoadSingleMessage(data, new_msg);
    }

    else if (task_name === 'clear-chat-area') {
        clearChatArea();
    }

    else if (task_name === "show-chat-user-phone-number") {
        const user_data = task.data;
        const user_id = user_data.user_id;
        const phone_number = user_data.phone_number;
        document.getElementById('chat-phone-label').innerText = phone_number;
        document.getElementById("chat-user-id").innerText = user_id;
    }

    else if (task_name === "get-socket-url") {
        StartWebSocket();
    }
}

function StartWebSocket() {
    const task = {
        name: "start-websocket",
        socket_url: CHAT_SOCKET_URL
    }
    worker.postMessage(task);
}


// CHAT FORM TO SEND THE MESSAGE TO THE WHATSAPP USER FROM THE LIVE ORDER PAGE.
const ChatForm = document.getElementById('chat-form');

// ADD EVENT LISTENER ON TIME OF SUBMIT OR SEND BUTTON.
ChatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const messageInput = document.getElementById('user-input');

    const task = {
        name: 'send-message-to-whatsapp',
        message: messageInput.value,
    }

    if (messageInput.value.replaceAll(' ', '') === "") {
        messageInput.setAttribute('class', 'form-control is-invalid')
    }

    else {
        worker.postMessage(task);
        messageInput.setAttribute('class', 'form-control')
        messageInput.value = "";
    }

})