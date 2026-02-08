let socket_url;

let audio = new Audio('/static/sound/notification.wav');

function playAudio() {
    while (true) {
        try {
            audio.play();
            break;
        }
        catch (error) {
            console.log(e)
            continue;
        }
    }
}

let order_received_audio = new Audio('/static/sound/order_received.wav')

function playOrderAudio() {
    while (true) {
        try {
            order_received_audio.play()
            break;
        }   
        catch (error) {
            console.log(error);
            continue;
        }
    }
}

let simple_audio = new Audio('/static/sound/no-sound.mp3')

function simpleAudioPlay() {
    while (true) {
        try {
            simple_audio.play()
            break;
        }
        catch (error) {
            continue;
        }
    }
}

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
                icon: '/static/assets/images/brand/Scan2FoodFabIcon.png',
                vibrate: [200, 100, 200],
            });
        }
    })

}

function RunWebSocket() {

    let allSeatSocket = new WebSocket(socket_url)

    allSeatSocket.onmessage = (e) => {
        let theatre_id = JSON.parse(document.getElementById('theatre-id').innerText)

        let eventData = JSON.parse(e.data)
        let updated_data = JSON.parse(eventData.updated_table_data);

        let order_theatre_id = updated_data.theatre_id

        simpleAudioPlay();

        if (order_theatre_id == theatre_id) {

            let seat_id = `seat-${updated_data.seat_id}`;
            let seat = document.getElementById(seat_id)

            let payment_panding = updated_data.payment_panding;

            if (payment_panding === false) {
                seat.setAttribute('class', 'seat paymentreceived');
                try {
                    const msg = updated_data.message.split("%0A%0A")[0];
                    showToast(updated_data.type, msg);
                }
                catch {
                    showToast(updated_data.type, updated_data.message);
                }

                sendNotification('Order Received', updated_data.message);
            }
            else if (payment_panding === true && updated_data.is_vacent === false) {
                seat.setAttribute('class', 'seat orderreceived');
                showToast(updated_data.type, updated_data.message);
                sendNotification('Order Received Payment Pending', updated_data.message);

            }

            let order_status = updated_data.is_vacent

            if (order_status == true) {
                seat.setAttribute('class', 'seat');
                playAudio();
            }

            else {
                if (updated_data.msg_typ === 'confirmation') {
                    playOrderAudio();
                }
            }

            showOrderData()
        }

    }

    allSeatSocket.onclose = (e) => {
        RunWebSocket()
    }
}

RunWebSocket()
