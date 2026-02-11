const showNotification = (notification_title, message) => {

    let notify = new Notification(notification_title, {
        body: message,
        icon: '/static/assets/images/brand/Scan2FoodFabIcon.png',
        vibrate: [200, 100, 200],
    });
}

// FUNCTIONS FOR ALL THE SOUND
function playSound(sound_name) {
    const task = { task_name: 'play-sound', sound_name: sound_name };
    postMessage(task)
}

// function for get request
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

// IT'S THE THEATRE ID
var theatre_id;

// ALL THE RUNNING ORDERS
var allRunningOrders = {}

// ALL THEATRE ORDERS
var theatreOrder = {}

function addTheatreOrder(order) {
    theatreOrder[order] = allRunningOrders[order];
    renderSingleOrder(order);
}

function removeTheatreOrder(seat_id) {
    const complete_id = `seat-id-${seat_id};`
    delete allRunningOrders[complete_id];
    delete theatreOrder[complete_id];

    const task = { task_name: 'order-deliverd', seat_id: seat_id }
    postMessage(task);
}

// SHOW THE ORDER ON UI
function renderSingleOrder(order) {
    const task = {
        task_name: 'render-single-order',
        order: order
    }

    postMessage(task);
}

// FORMATED TIME
function getFormattedDateTime() {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    const now = new Date();

    const day = String(now.getDate()).padStart(2, '0');
    const month = months[now.getMonth()];
    const year = now.getFullYear();

    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12; // convert to 12-hour format
    const formattedHours = String(hours).padStart(2, '0');

    return `${day}-${month}-${year}|${formattedHours}:${minutes} ${ampm}`;
}

// RENDER SINGLE ORDER
function renderOrderData() {
    // get the Theatre Order
    for (let order in allRunningOrders) {
        const order_detail = allRunningOrders[order]
        if (order_detail.theatre_id === theatre_id) {
            // add the order in theatre order
            addTheatreOrder(order_detail)
        }
    }

}

// GET ALL THE ORDER USING API
async function getAllRunningOrders(t_id) {
    theatre_id = t_id;
    const url = `/theatre/api/live-orders`
    allRunningOrders = await getRequest(url);
    renderOrderData()
}

// all the socket functions...
function runWebSocket(socket_url) {
    // Add API key to WebSocket URL
    const ws_key = '05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM';
    const socket_url_with_key = `${socket_url}?key=${ws_key}`;
    
    let allSeatSocket = new WebSocket(socket_url_with_key)

    allSeatSocket.onopen = (e) => {
        const connected_data = {'theatre_id': theatre_id}
        allSeatSocket.send(JSON.stringify(connected_data))

    }

    allSeatSocket.onmessage = (e) => {
        // get the event data
        const eventData = JSON.parse(e.data);
        // get exect data of event "seen", "order_confirmed", "order-deliverd"
        let updated_data = JSON.parse(eventData.updated_table_data)

        // upcomming order and it's order id and seat id
        let order_theatre_id = updated_data.theatre_id;

        // play the normal sound
        playSound('normal')

        if (order_theatre_id === theatre_id) {
            const msg_typ = updated_data.msg_typ

            if (msg_typ === "confirmation") {
                // new order received...
                const seat_id = updated_data.seat_id;
                const order_id = updated_data.order_id;
                const seat_name= updated_data.seat_name.split("|")[1];
                const hall_name= updated_data.seat_name.split("|")[0];
                const order = {
                    seat_id: seat_id,
                    seat_name: seat_name,
                    hall_name: hall_name,
                    is_vacent: false,
                    theatre_id: order_theatre_id,
                    theatre_name: updated_data.theatre_name,
                    is_shown: false,
                    payment_time: getFormattedDateTime(),
                    amount: updated_data.amount,
                    order_id: order_id,
                    max_time: updated_data.max_time,
                    payment_method: updated_data.payment_method,
                    payment_status: updated_data.payment_status,
                }

                // add the order to the all orders and update the ui
                addTheatreOrder(order)
                playSound('new-order-arived')
                showNotification('New Order', `New Order Received on Seat: ${hall_name}, ${seat_name}`);
            }
            // this is code which have to run for this theatre...

            else if (msg_typ === 'order_seen') {
                const seat_id = updated_data.seat_id;

                // an order is seen
                const task = { task_name: 'make-order-seen', seat_id: seat_id };
                postMessage(task);
            }

            else if (msg_typ === "Delivered") {
                const seat_id = updated_data.seat_id
                removeTheatreOrder(seat_id);
                playSound('order-deliverd');
            }

            else if (msg_typ === "Cancelation") {
                const seat_id = updated_data.seat_id;
                removeTheatreOrder(seat_id);
                playSound('order-deliverd');
            }

        }
    }

    allSeatSocket.onclose = (e) => {
        runWebSocket(socket_url)
    }
}
// socket codes ends here

// worker intake
onmessage = (e) => {
    const task = e.data;
    const task_name = task.task_name;

    if (task_name === 'get-all-orders') {
        const theatre_id = task.theatre_id;
        getAllRunningOrders(theatre_id);
    }

    else if (task_name === 'start-websocket') {
        const socket_url = task.socket_url
        runWebSocket(socket_url);
    }
}