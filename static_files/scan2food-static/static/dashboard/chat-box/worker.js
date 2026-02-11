function SortAllChatUsers() {
    // Function to parse "02-Sep-2025 10:34 AM" into Date
    function parseDate(str) {
        return new Date(str);
    }

    // Sort by msg_time
    let sortedEntries = Object.entries(AllChatUsers).sort((a, b) => {
        return parseDate(a[1].msg_time) - parseDate(b[1].msg_time);
    });

    // Convert back to object
    let sortedData = Object.fromEntries(sortedEntries);
    return sortedData
}


var CSRF_TOKEN;
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

// FUNCTION TO GET DATA FROM GET REQUEST
async function getRequest(url) {

    return fetch(url)
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

async function getAllChatUsers() {
    AllChatUsers = [];
    // LOAD ALL THE CUSTOMERS IN UI LAVEL
    const all_user_api = '/chat-box/chat-users'
    let all_chat_users = await getRequest(all_user_api)

    AllChatUsers = all_chat_users;
    all_chat_users = {}

    for (let i in AllChatUsers) {
        const chat_user = AllChatUsers[i]

        if (chat_user.reply_required) {
            ChatCount += 1
        }

        all_chat_users[i] = AllChatUsers[i]
    }

    AllChatUsers = all_chat_users;

    UpdateChatButtonCount();
}

var socket;
// FUNCTION CONNECT THE WEBSOCKET AND PERFORM ALL THE SOCKET RELATED CODE
function connectWebsocket(socket_url) {
    ChatCount = 0
    // Add API key to WebSocket URL
    const ws_key = 'A0B9sna1Pdio-1MdXHG8kQJwuC_45Ok2ZmlQbS_0B-U';
    const socket_url_with_key = `${socket_url}?key=${ws_key}`;
    
    socket = new WebSocket(socket_url_with_key);
    socket.onopen = async (e) => {
        await getAllChatUsers();
    }

    socket.onmessage = async (e) => {

        const eventData = JSON.parse(e.data);

        const dataContains = eventData['data-contains']

        if (dataContains === "phone-number-messages") {
            const messages = eventData['messages'];
            const phone_number = eventData['phone-number'];

            AllChatUsers[`phone-${phone_number}`]['user_messages'] = messages;
            LoadChats(phone_number)

        }

        else if (dataContains === "new-outgoing-message") {

            const phone_number = eventData['phone_number'];
            const phone_key = `phone-${phone_number}`;
            const message_data = eventData['message_data'];
            const theatre_id = eventData['theatre_id'];
            const msg_time = eventData['msg_time'];

            const msg_type = message_data.msg_type;

            if (!Object.keys(AllChatUsers).includes(phone_key)) {

                const new_phne_data = {
                    continue_chat: true,
                    hall_name: eventData['hall_name'],
                    phone_number: phone_number,
                    pk: eventData['pk'],
                    reply_required: false,
                    seat_id: eventData['seat_id'],
                    seat_name: eventData['seat_name'],
                    theatre_id: theatre_id,
                    theatre_name: eventData['theatre_name'],
                    user_messages: []
                }

                AllChatUsers[phone_key] = new_phne_data;
            }

            if (AllChatUsers[phone_key]['reply_required']) {
                if (msg_type === 'OUTGOING') {
                    ChatCount -= 1;
                    AllChatUsers[phone_key]['reply_required'] = false;
                    UpdateChatButtonCount();
                }
            }

            else {
                if (msg_type === 'INCOMING') {
                    ChatCount += 1;
                    AllChatUsers[phone_key]['reply_required'] = true;
                    UpdateChatButtonCount();
                }
            }

            AllChatUsers[phone_key]['msg_time'] = msg_time;
            // UPDATE THE MESSAGE ON UI AND SAVE IN ALL CHAT USERS
            AllChatUsers[phone_key]['user_messages'].unshift(message_data)

            // UPDATE ON THE UI
            const new_task = {
                task: 'update-new-message',
                message: message_data,
                phone_number: phone_number
            }
            postMessage(new_task);

        }
        // else {
        //     console.log(eventData);
        // }
    }

    socket.onclose = (e) => {
        connectWebsocket(socket_url);
    }
}


// ALL THE GLOBAL VARIABLES AND DATA STORE IN THESE VARIABLES
var AllChatUsers;
var ChatCount;
ChatCount = 0;


// UPDATE THE MESSAGE COUNT
function UpdateChatButtonCount() {
    const task = {
        task: 'update-chat-count',
        chat_count: ChatCount
    }
    self.postMessage(task);
}


// LOAD THE MESSAGES ON UI
function LoadChats(phone_number) {
    // LOAD MESSAGES IN UI LAVEL

    const data_key = `phone-${phone_number}`
    const data_value = AllChatUsers[data_key]
    const task = {
        task: 'load-chats',
        phone_number: phone_number,
        hall_name: data_value['hall_name'],
        seat_name: data_value['seat_name'],
        messages: data_value['user_messages'],
        theatre_name: data_value['theatre_name'],
    };

    postMessage(task);
}

// WORKER INCOMING MESSAGES
self.onmessage = (e) => {
    const data = e.data;
    const task = data.task;

    if (task === "save-theatre-id") {
        const theatre_id = data.theatre_id
        const csrf_token = data.csrf_token
        CSRF_TOKEN = csrf_token
    }
    else if (task === "start-websocket") {
        const socket_url = data.socket_url;
        connectWebsocket(socket_url);
    }

    else if (task === 'load-all-users') {
        AllChatUsers = SortAllChatUsers();

        const new_task = {
            task: 'load-all-users',
            chat_users: AllChatUsers
        }
        postMessage(new_task);
    }

    else if (task === 'get-user-messages') {
        const phone_key = data.phone_key;

        const user_data = AllChatUsers[phone_key];

        const all_messages = user_data.user_messages;

        if (all_messages.length === 0) {
            // TRY TO GET THE MESSAGES FROM SOCKET
            const socket_task = {
                task: 'get-user-messages',
                phone_number: user_data.phone_number
            }
            socket.send(JSON.stringify(socket_task))
        }
        else {
            LoadChats(user_data.phone_number)
        }
    }

    else if (task === 'send-message-to-whatsapp') {
        const message = data.message;
        const phone_number = data.phone_number;

        // // NOW GOING TO SEND THE DATA TO WEBSOCKET
        // socket.send(JSON.stringify(newTask));
        const message_url = `/chat-box/send-whatsapp-message`
        const post_data = {
            phone_number: phone_number,
            message: message
        }

        PostRequest(message_url, post_data);
    }
}
