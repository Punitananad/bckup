var ALL_CHAT = []
var USER_PHONE_NUMBER;
var CSRF_TOKEN;

function LoadSingleMessage(chat_data, new_msg) {
    const task = {
        name: 'load-single-chat',
        data: chat_data,
        new_msg: new_msg
    }
    postMessage(task);
}

function LoadChatUserPhoneNumber(data) {
    const task = {
        name: 'show-chat-user-phone-number',
        data: data
    }
    postMessage(task);
}

function clearChatArea() {
    const task = {
        name: 'clear-chat-area'
    }
    postMessage(task);
}

function LoadAllChats(order_id) {
    if (ALL_CHAT.length === 0) {
        clearChatArea();
        const stream_url = `/chat-box/get-chat-from-order-id/${order_id}`;
        const eventStream = new EventSource(stream_url);

        eventStream.onmessage = (e) => {
            const chat_data = JSON.parse(e.data);

            if ('phone_number' in chat_data) {
                USER_PHONE_NUMBER = chat_data.phone_number;
                LoadChatUserPhoneNumber(chat_data);
            }
            else {
                ALL_CHAT.push(chat_data);
                LoadSingleMessage(chat_data, false);
            }
        }

        eventStream.onerror = (e) => {
            eventStream.close();
            getSocketUrl();
        }
    }
}


onmessage = (event) => {
    const task = event.data;
    const task_name = task.name

    switch (task_name) {
        case ('load-all-chats'):
            const order_id = task.orderId;
            LoadAllChats(order_id);
            break;

        case ('start-websocket'):
            const socket_url = task.socket_url
            connectWebsocket(socket_url);
            break;

        case ('send-message-to-whatsapp'):
            const message = task.message;
            const message_url = `/chat-box/send-whatsapp-message`
            const post_data = {
                phone_number: USER_PHONE_NUMBER,
                message: message
            }

            PostRequest(message_url, post_data);
            break;
        
        case ('load-csrf-token'):
            CSRF_TOKEN = task.csrf_token
            break;
    }
}





/// socket connection
function getSocketUrl() {
    const task = {
        name: "get-socket-url"
    }
    postMessage(task);
}

function connectWebsocket(socket_url) {
    CHAT_SOCKET = new WebSocket(socket_url);
    CHAT_SOCKET.onmessage = async (e) => {
        const eventData = JSON.parse(e.data);
        if (eventData['phone_number'] === USER_PHONE_NUMBER) {
            const chat_data = eventData.message_data
            LoadSingleMessage(chat_data, true);
        }
    }
}

// function to hit the post request
async function PostRequest(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(data),
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            return data;
        })
        .catch(function (error) {
            console.error('Error:', error);
            throw new Error('Failed to fetch data');
        });
}