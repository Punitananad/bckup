let socket_url

if (window.location.href.includes('https')) {
    socket_url = `wss://${window.location.host}/ws/all-messages/`
}
else {
    socket_url = `ws://${window.location.host}/ws/all-messages/`
}

function RunWebSocket() {

    const chatForm = document.getElementById('chat-form');
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault(); //prevent default submition
        const message = document.getElementById('user-input').value;
        const phone_number = document.getElementById('selected-phone').innerText;

        if (phone_number === "" || message.replaceAll(" ", "") === "") {
            alert('Please Select a chat or enter a message')
            return;
        }
        const socket_data = { 'phone_number': phone_number, 'message': message }

        chatSocket.send(JSON.stringify(socket_data));
        document.getElementById('user-input').value = ""
    })

    let chatSocket = new WebSocket(socket_url);

    chatSocket.onmessage = (e) => {
        const socket_data = e.data;

        let chat_data = JSON.parse(socket_data);

        chat_data = chat_data.updated_message;
        chat_data = JSON.parse(chat_data);

        const phone_number = chat_data.phone_number
        const phn_li = document.getElementById(phone_number);
        if (phn_li !== null) {
            phn_li.remove()
        }

        const new_phn = document.createElement('li');
        new_phn.setAttribute('class', 'list-group-item')
        new_phn.innerHTML = `
        ${phone_number}
        <span class="text-muted small">${chat_data.msg_tym}</span>
        <span class="badge bg-success ms-2">New</span>
        `;
        new_phn.setAttribute('id', phone_number);

        new_phn.addEventListener('click', () => {
            loadChat(phone_number);
        })

        const phn_list = document.getElementById('phone-list');
        phn_list.prepend(new_phn)

        if (document.getElementById('selected-phone').innerText == phone_number) {
            new_phn.setAttribute('class', 'list-group-item active')
            ApendSingleMessage(chat_data)
        }


        // show toast message
        showToast('bg-success', phone_number, chat_data.message);


    }

    chatSocket.onclose = (e) => {
        RunWebSocket()
    }
}
// websocket is connected...

RunWebSocket()

// GET ALL USERS FORM THE SSE
// STARTING A WEB WORKER

// FUNCTION GET ALL THE PHONE NUMBER
function getAllPhoneNumber() {
    const task = { 'task': 'get_all_phone_number' }
    worker.postMessage(task)
}

// FUNCTION LOAD THE CHAT
function loadChat(phone_number) {

    const PhoneList = document.getElementById('phone-list');
    activeLi = PhoneList.getElementsByClassName('active');
    document.getElementById('chat-box').innerHTML = ''
    document.getElementById('selected-phone').innerText = phone_number;

    for (let i = 0; i < activeLi.length; i++) {
        const itm = activeLi[i].setAttribute('class', 'list-group-item')
    }

    const thisPhone = document.getElementById(phone_number);
    thisPhone.setAttribute('class', 'list-group-item active')

    // Load all chats
    const task = { 'task': 'get-user-chat', 'phone_number': phone_number }

    worker.postMessage(task);

    $("#msg-card-box").modal('show');
}

function AddSingleMessage(message) {
    const msgBox = document.getElementById('chat-box');
    const msg = document.createElement('div');

    const msg_typ = message.msg_type;
    if (msg_typ === 'message') {
        msg.setAttribute('class', 'd-flex mb-2');
        msg_txt = document.createElement('div');
        msg_txt.setAttribute('class', 'bg-light rounded p-2');
    }
    else {
        msg.setAttribute('class', 'd-flex justify-content-end mb-2');
        msg_txt = document.createElement('div');
        msg_txt.setAttribute('class', 'bg-primary text-white small rounded p-2');
        msg_txt.setAttribute('style', 'max-width: 80%; word-wrap: break-word;')
    }

    msg_txt.innerHTML = `
    ${message.message}
    <div class="text-muted small text-end mt-1">${message.msg_tym}</div>
    `;
    msg.appendChild(msg_txt);
    msgBox.prepend(msg);

    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;

}

function ApendSingleMessage(message) {

    const msgBox = document.getElementById('chat-box');
    const msg = document.createElement('div');

    const msg_typ = message.msg_type;
    if (msg_typ === 'message') {
        msg.setAttribute('class', 'd-flex mb-2');
        msg_txt = document.createElement('div');
        msg_txt.setAttribute('class', 'bg-light rounded p-2');
    }
    else {
        msg.setAttribute('class', 'd-flex justify-content-end mb-2');
        msg_txt = document.createElement('div');
        msg_txt.setAttribute('class', 'bg-primary text-white rounded p-2 small');
        msg_txt.setAttribute('style', 'max-width: 80%; word-wrap: break-word;')
    }

    msg_txt.innerHTML = `
    ${message.message}
    <div class="text-muted small text-end mt-1">${message.msg_tym}</div>
    `;
    msg.appendChild(msg_txt);
    msgBox.append(msg);

    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;

}


const worker = new Worker('/static/chatBox/worker.js')

getAllPhoneNumber()

worker.onmessage = function (e) {
    const data = e.data;
    if (data.task === 'add_phone_number') {

        const phoneList = document.getElementById('phone-list');
        const newPhone = document.createElement('li');
        const userDetail = data.user_data
        const phone_number = userDetail.phone_number
        const last_tym = userDetail.last_message_tym;
        console.log(last_tym)
        newPhone.setAttribute('class', 'list-group-item');
        newPhone.setAttribute('id', phone_number);

        newPhone.innerHTML = `${phone_number}
        <span class="text-muted small float-end">${last_tym}</span>`
        newPhone.addEventListener('click', () => {
            loadChat(phone_number);
        })
        phoneList.appendChild(newPhone);
    }

    if (data.task === 'show-messages') {
        const message = data.message;
        AddSingleMessage(message);
    }
}



function scrollToBottom() {
    const chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}


const chatModal = document.getElementById('msg-card-box');

chatModal.addEventListener('shown.bs.modal', function () {
    scrollToBottom();
});