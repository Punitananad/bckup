// worker is initilited


// FUNCTION TO SEND ALL PHONE NUMBER ONE BY ONE TO
function getAllPhoneNumber() {
    // URL TO GET ALL THE PHONE NUMBERS
    const sse_url = '/chat-box/sse-chat-users-stream'
    // start the sse connection
    const eventSource = new EventSource(sse_url);
    
    eventSource.onmessage = (e) => {
        try {
            const user_data = JSON.parse(e.data);
            const task = {'task':'add_phone_number', 'user_data': user_data }
            postMessage(task)
        }
        catch (error) {
            console.log('error....\n =>', error)
        }
    }

    eventSource.onerror = (e) => {
        eventSource.close();
        postMessage({ name: 'error', message: 'SSE connection closed due to error.', data: [] });
    };
}

function loadChat(phone_number){
    // url to get all chats
    const sse_url = `/chat-box/sse-user-chat?phone_number=${phone_number}`
    const eventSource = new EventSource(sse_url);

    eventSource.onmessage = (e) => {
        try {
            const message = JSON.parse(e.data);
            const task = {'task': 'show-messages', 'message': message}
            postMessage(task)
        }
        catch (error) {
            console.log('error   ->', error)
        }
    }

    eventSource.onerror = (e) => {
        eventSource.close();
        postMessage({name: 'error', message: 'SSE connection closed due to error.', data: [] })
    }
}

self.onmessage = function (e) {
    const data = e.data;

    const task = data.task;

    if (task === 'get_all_phone_number') {
        getAllPhoneNumber();
    }

    if (task === 'get-user-chat') {
        const phone_number = data.phone_number;
        loadChat(phone_number);
    }

}