// adding the style to the button
const payment_button = document.getElementsByClassName('razorpay-payment-button')[0];
payment_button.classList.add('btn');
payment_button.classList.add('btn-primary');

let order_id = JSON.parse(document.getElementById('order-id').innerText);

let websocket_url;
if (window.location.host.includes('https')){
    websocket_url = `wss://${window.location.host}/ws/payment-socket/${order_id}/`;
}
else {
    websocket_url = `ws://${window.location.host}/ws/payment-socket/${order_id}/`;
}

let paymentSocket = new WebSocket(websocket_url);

