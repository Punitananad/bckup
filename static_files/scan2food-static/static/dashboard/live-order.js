const worker_script_url = '/static/dashboard/live-order-worker.js';

const worker = new Worker(worker_script_url);

var connected_theatres = []

// It Load All the Orders
function loadAllOrders() {
    task_name = 'get-all-orders';
    worker.postMessage({ task: task_name });
}

// Parse payment_time to Date
function parsePaymentTime(str) {
    const [datePart, timePart] = str.split('|');
    return new Date(`${datePart} ${timePart}`);
}

// It Updates the UI as per Every Order
function loadSingleOrder(order_detail) {
    const theatre_id = order_detail.theatre_id;
    const theatre_name = order_detail.theatre_name;

    let payment_time = order_detail.payment_time;

    payment_time = payment_time.split('|')[1]

    let theatre_li = document.getElementById(`theatre-id-${theatre_id}`);

    if (theatre_li === null) {
        // create a new li
        theatre_li = document.createElement('li');
        theatre_li.setAttribute('class', 'nav-item py-2');
        theatre_li.setAttribute('id', `theatre-id-${theatre_id}`);

        // cosnt anchor tag
        const theatre_li_html = `
                    <a href="#" class="d-flex align-items-center text-start mx-3 ms-0">
                        <div class="shadow p-3 brdr-left-2px">
                            <span class="badge bg-danger connection-status-badge">
                                Not Connected
                            </span>
                            <h6 class="mt-n1 mb-0 theatre-name-label border-bottom pb-2 mb-2">${theatre_name}  </h6>
                            
                            <p class="mb-0 text-muted small">Pending Orders:
                                <strong class="text-primary fw-bold order-count-label">
                                    0
                                </strong>
                            </p>
                            <p class="mb-0 text-muted small">Last Order Time:
                                <strong class="text-primary fw-bold last-order-time-label">
                                    
                                </strong>
                            </p>
                            <p class="mb-0 text-muted small">Unseen Orders:
                                <strong class="text-primary fw-bold unseen-orders-label">
                                    0
                                </strong>
                            </p>
                            <p class="mb-0 text-muted small d-none">Time Remaint:
                                <strong class="text-primary fw-bold timer">
                                    0
                                </strong>
                            </p>
                            
                        </div>
                    </a>
        `
        theatre_li.innerHTML = theatre_li_html;

        if (order_detail.live_connection) {
            const connectionBadge = theatre_li.getElementsByClassName('connection-status-badge')[0];

            connectionBadge.setAttribute('class', 'badge bg-success connection-status-badge');
            connectionBadge.innerText = 'Connected';
        }

        const all_theatre_box = document.getElementById('all-theatres');
        all_theatre_box.appendChild(theatre_li);

        // add Event Listener to show This Theatre Orders;
        theatre_li.addEventListener('click', function () {
            loadTheatreOrders(theatre_id);
        })
    }

    // add the order count
    const order_count_label = theatre_li.querySelector('.order-count-label');
    let order_count = parseInt(order_count_label.innerText);

    order_count += 1;
    order_count_label.innerText = order_count;

    // all the time of last order
    const last_order_time_label = theatre_li.querySelector('.last-order-time-label');

    if (last_order_time_label.innerText.replaceAll(" ", "") === "") {
        last_order_time_label.innerText = payment_time;
    }

    // unseen orders
    const unseen_orders_label = theatre_li.querySelector('.unseen-orders-label');
    unseen_orders_label.innerText = order_detail.unseen_orders;


}

function loadTheatreOrders(theatre_id) {

    // get all orders of single Theatre by Id
    worker.postMessage({
        task: 'get-all-orders-of-theatre',
        theatre_id: theatre_id
    })
}

function showTheatreOrder(theatre_data) {
    // show the modal
    document.getElementById('orderListPopUpLabel').innerText = theatre_data.theatre_name;

    // empty all the orders
    const order_list = document.getElementById('all-orders-list');
    order_list.innerHTML = '';
    const orders = theatre_data.orders;

    for (let i = 0; i < orders.length; i++) {
        const order = orders[i];
        const tr = document.createElement('tr');
        const seat = `${order.hall_name} (${order.seat_name})`;
        const payment_method = order.payment_method;
        const payment_status = order.payment_status;
        const order_time = order.payment_time.split('|')[1];
        const amount = order.amount;
        const view_status = order.is_shown;

        const tr_html = `
            <td class="text-center">${seat}</td>
            <td class="text-center">${order_time}</td>
            <td class="text-center">${amount}</td>
            <td class="text-center">${payment_method}</td>
            <td class="text-center">${payment_status}</td>
            <td class="text-center">${view_status ? '<span class="badge bg-success"> Seen <span>' : '<span class="badge bg-danger"> Unseen </span>'}</td>
            <td class="text-center">
                <button class="btn btn-primary btn-sm">
                    View
                </button>
            </td>
            `
        tr.innerHTML = tr_html;
        const view_btn = tr.querySelector('button');
        view_btn.addEventListener('click', async function () {

            await openOrderProfile(order.order_id);
            document.getElementById('orderPopUpLabel').innerText = seat;

            $("#orderPopUp").modal('show');

        })
        order_list.appendChild(tr);
    }

    $("#orderListPopUp").modal('show');
}

function delete_order(order_id, theatre_id) {
    const task = { task: 'delete-order', order_id: order_id, theatre_id: theatre_id };
    worker.postMessage(task);
}

function updateSeenOrder(order_id, theatre_id) {
    const task = { task: 'order-seen', order_id: order_id, theatre_id: theatre_id };
    worker.postMessage(task);
}

loadAllOrders();


worker.onmessage = (e) => {
    const data = e.data;
    const task_name = data.task;

    if (task_name === 'add-order') {
        const order_data = data.order_data;
        loadSingleOrder(order_data);
    }

    else if (task_name === 'theatre-orders') {
        const theatre_data = data.order_data;
        showTheatreOrder(theatre_data);
    }

    else if (task_name === 'update-deleted-order') {
        const order_count = data.order_count;
        const last_order_time = data.last_order_time;
        const theatre_id = data.theatre_id
        const seen_orders = data.seen_orders

        // get the theatre li
        const theatre_li = document.getElementById(`theatre-id-${theatre_id}`)

        if (order_count === 0) {
            // remove the theatre
            theatre_li.remove();
        }

        else if (last_order_time !== undefined) {

            const tym = last_order_time.split("|")[1]
            theatre_li.getElementsByClassName('last-order-time-label')[0].innerText = tym;

            theatre_li.getElementsByClassName('order-count-label')[0].innerText = order_count;
        }

        else if (seen_orders !== undefined) {
            const seen_order_label = theatre_li.getElementsByClassName('unseen-orders-label')[0]
            seen_order_label.innerText = seen_orders
        }
    }

}















































































function updateLiveConnection(theatres) {
    for (let i = 0; i < theatres.length; i++) {
        try {
            const theatre_id = `theatre-id-${theatres[i]}`
            const theatreLi = document.getElementById(theatre_id);
            const connectionBadge = theatreLi.getElementsByClassName('connection-status-badge')[0];

            connectionBadge.setAttribute('class', 'badge bg-success connection-status-badge');
            connectionBadge.innerText = 'Connected';
        }   
        catch (error) {
            
        }
    }
}


function formatCurrentTime() {
    const now = new Date();

    const day = String(now.getDate()).padStart(2, '0');
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const month = monthNames[now.getMonth()];
    const year = now.getFullYear();

    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;  // convert to 12-hour format

    const formatted = `${day}-${month}-${year}|${String(hours).padStart(2, '0')}:${minutes} ${ampm}`;
    return formatted;
}



// connect with the socket...
let socket_url;

const seen_audio = new Audio('/static/sound/delivered.wav');
const new_order_audio = new Audio('/static/sound/order_received.wav');
const delivery_sound = new Audio('/static/sound/notification.wav')

// let order_received_audio = new Audio('https://guru-sevak-singh.github.io/scan2food-static/static/sound/order_received.wav')

if (window.location.href.includes('https')) {
    socket_url = `wss://${window.location.host}/ws/all-seat-datasocket/`
}
else {
    socket_url = `ws://${window.location.host}/ws/all-seat-datasocket/`
}

const sendNotification = (notification_title, message) => {
    Notification.requestPermission().then(perm => {
        if (perm === 'denied') {
            console.error('Please allow notifications to receive notifications');
        }
        else if (perm === 'granted') {
            let notify = new Notification(notification_title, {
                body: message,
                icon: 'https://guru-sevak-singh.github.io/scan2food-static/static/assets/images/brand/Scan2FoodFabIcon.png',
                vibrate: [200, 100, 200],
            });
        }
    })

}

function RunWebSocket() {

    let allSeatSocket = new WebSocket(socket_url)

    allSeatSocket.onopen = (e) => {
        const connected_data = { 'theatre_id': 'admin' }
        allSeatSocket.send(JSON.stringify(connected_data))
    }

    allSeatSocket.onmessage = (e) => {

        let eventData = JSON.parse(e.data)
        let updated_data = JSON.parse(eventData.updated_table_data);

        const msg_typ = updated_data.msg_typ;

        if (msg_typ === 'all-connected-theatres') {
            const all_connected_theatres = updated_data.connected_theatres;

            const theatres = [...new Set(all_connected_theatres)];
            connected_theatres = theatres;
            
            setTimeout(() => {
                updateLiveConnection(theatres);
            }, 2000);
        }

        else if (msg_typ === 'connected_theatre') {
            const theatre_id = updated_data.connected_theatre_id
            const theatreLi = document.getElementById(`theatre-id-${theatre_id}`);
            const connectionBadge = theatreLi.getElementsByClassName('connection-status-badge')[0];

            connectionBadge.setAttribute('class', 'badge bg-success connection-status-badge');
            connectionBadge.innerText = 'Connected';
        }

        else if (msg_typ === 'disconnected_theatre') {
            const theatre_id = updated_data.disconnected_theatre_id;
            const theatreLi = document.getElementById(`theatre-id-${theatre_id}`)

            const connectionBadge = theatreLi.getElementsByClassName('connection-status-badge')[0];
            
            connectionBadge.setAttribute('class', 'badge bg-danger connection-status-badge');
            connectionBadge.innerText = 'Not Connected';
            
            connected_theatres.splice(connected_theatres.indexOf(theatre_id), 1);

        }

        else if (msg_typ === 'confirmation') {
            // create order data and save to the order data to worker page...
            // create the order data

            try {
                new_order_audio.play();
            }
            catch {
                console.log('error')
            }

            var live_connection = false

            if (connected_theatres.includes(updated_data.theatre_id)) {
                live_connection = true
            }
            const order_data = {
                order_id: updated_data.order_id,
                theatre_id: updated_data.theatre_id,
                payment_time: formatCurrentTime(),
                hall_name: updated_data.seat_name.split("|")[0],
                seat_name: updated_data.seat_name.split("|")[1],
                seat_id: updated_data.seat_id,
                amount: updated_data.amount,
                is_shown: false,
                theatre_name: updated_data.theatre_name,
                order_amount: updated_data.amount,
                payment_method: updated_data.payment_method,
                payment_status: updated_data.payment_status,
                live_connection: live_connection
            }

            const task = { task: 'add-new-order', order_data: order_data };
            worker.postMessage(task)
        }

        else if (msg_typ === 'Delivered') {
            try {
                delivery_sound.play();
            }
            catch {
                console.log('error')
            }
            // ṛemove the order from the order data in worker script
            const order_id = updated_data.order_id;
            const theatre_id = updated_data.theatre_id;

            delete_order(order_id, theatre_id)
        }

        else if (msg_typ === 'Cancelation') {
            // remove the order from the order data in worker script
            const order_id = updated_data.order_id;
            const theatre_id = updated_data.theatre_id;

            delete_order(order_id, theatre_id)
        }

        else if (msg_typ === "order_seen") {
            try {
                seen_audio.play();
            }
            catch {
                console.log('error')
            }
            const order_id = updated_data.order_id;
            const theatre_id = updated_data.theatre_id;

            updateSeenOrder(order_id, theatre_id)
        }

    }

    allSeatSocket.onclose = (e) => {
        RunWebSocket()
    }
}

RunWebSocket()
