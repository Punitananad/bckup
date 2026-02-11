// adding the style to the button
const payment_button = document.getElementsByClassName('razorpay-payment-button')[0];
payment_button.classList.add('btn');
payment_button.classList.add('btn-primary');

let order_id = JSON.parse(document.getElementById('order-id').innerText);

// WebSocket API key
const ws_key = 'vy8ALNb9ev6DvTFGHv9IC3RgQ0xL5shqNmnFmDEHNqM';

let websocket_url;
if (window.location.host.includes('https')){
    websocket_url = `wss://${window.location.host}/ws/payment-socket/${order_id}/?key=${ws_key}`;
}
else {
    websocket_url = `ws://${window.location.host}/ws/payment-socket/${order_id}/?key=${ws_key}`;
}

let paymentSocket = new WebSocket(websocket_url);

