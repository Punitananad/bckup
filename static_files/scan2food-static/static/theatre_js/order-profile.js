function showTax() {
    let order_area = document.getElementById('order-items');

    let sub_amount = parseFloat(document.getElementById('sub-amount').innerText);

    let all_taxes = order_area.querySelectorAll('.tax-perscantage');

    let grand_sum = 0
    grand_sum += sub_amount;

    let tax_amounts = order_area.querySelectorAll('.tax-amount')
    for (let i = 0; i < all_taxes.length; i++) {

        let tax_perscantage = parseFloat(all_taxes[i].innerText)

        let tax_amount = sub_amount * (tax_perscantage / 100)

        tax_amounts[i].innerText = tax_amount
        grand_sum += tax_amount
    }

    grand_sum = grand_sum.toFixed(2)
    let amount_titles = document.querySelectorAll('.amount-with-tax')

    amount_titles.forEach(element => {
        element.innerText = grand_sum;
    });


}

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


function printKot(btn) {
    let order_id = btn.getAttribute('order_id');
    window.open(`/theatre/print-kot/${order_id}`, "", "width=600, height=600");
    UpdateSeatView(btn);
}

function printBill(btn) {
    let order_id = btn.getAttribute('order_id');
    window.open(`/theatre/print-bill/${order_id}`, "", "width=600, height=600");
}

function createOrderTab(order_data) {
    document.getElementById('delivery-detail-box').setAttribute('class', 'd-none');
    if (order_data.order_detail.food_delivered === false) {
        document.getElementById('delivery-status').innerHTML = `<i class="fa fas fa-clock text-danger mb-0 me-1"></i>Delivery Pending`;
        document.getElementById('order-deliver-button').setAttribute('style', '');
    }
    else {
        document.getElementById('delivery-status').innerHTML = `<i class="fa fas fa-check-circle text-success mb-0 me-1"></i> Order Delivered`;
        document.getElementById('order-deliver-button').style.display = 'none';
        document.getElementById('delivery-detail-box').setAttribute('class', 'd-flex justify-content-between');
        document.getElementById('delivery-detail-box-value').innerText = order_data.order_detail.delivery_time;
    }

    document.getElementById('order-deliver-button').setAttribute('order-id', order_data.order_detail.order_id)
    document.getElementById('order-id').innerText = `#${order_data.order_detail.order_id}`;
    document.getElementById('seat-name').innerText = order_data.seat;

    document.getElementById('items-tab').setAttribute('seat-id', order_data.seat_id);
    document.getElementById('kot-button').setAttribute('seat-id', order_data.seat_id);

    document.getElementById('order-date').innerText = order_data.order_detail.order_date;
    document.getElementById('order-time').innerText = order_data.order_detail.order_time;
    let phone_number = order_data.order_detail.phone_number

    if (phone_number == "") {
        document.getElementById('phone-number').innerHTML = `
        <button class="btn btn-success btn-sm" onclick="getPhonNumberByOrderId('${order_data.order_detail.order_id}')">Get PhoneNumber</button>`
    }
    else {
        document.getElementById('phone-number').innerText = phone_number;
    }


    if (order_data.order_detail.payment_pending === true) {
        payment_status = `<i class="fa fas fa-clock text-danger mb-0 me-1"></i> ${order_data.order_detail.payment_status}`;
        document.getElementById('panding-amount-heading').innerText = 'Pending Amount';
        document.getElementById('payment-tab-panding-amount-heading').innerText = 'Pending Amount';
        document.getElementById('panding-amount-heading-value').innerText = 0;
        document.getElementById('payment-tab-panding-amount-value').setAttribute('class', 'amount-with-tax');
    }
    else {
        payment_status = `<i class="fa fas fa-check-circle text-success mb-0 me-1"></i> ${order_data.order_detail.payment_status}`;
        document.getElementById('panding-amount-heading').innerText = 'Amount Paid';
        document.getElementById('payment-tab-panding-amount-heading').innerText = 'Amount Paid';
        document.getElementById('panding-amount-heading-value').innerText = order_data.order_detail.amount;
        document.getElementById('payment-tab-panding-amount-value').innerText = order_data.order_detail.amount;
        document.getElementById('payment-method-value').innerHTML = order_data.order_detail.payment_method;
    }

    if (order_data.order_detail.is_shown == true) {
        document.getElementById('order-shown').innerHTML = `Order Seen`;
    }
    else {
        document.getElementById('order-shown').innerHTML = `Order Not Seen Yet !`;
    }

    document.getElementById('payment-status').innerHTML = payment_status
    document.getElementById('payment-tab-payment-status').innerHTML = payment_status

}

function createCartTab(order_data) {
    let cart_items = order_data.order_items;
    let all_tax_area_html = document.getElementById('all-tax-area').innerHTML
    document.getElementById('order-items').innerHTML = ""

    // ADDING NOTES SECTION
    document.getElementById('order-items').innerHTML += `
                <div class="row mb-2 order-item order-item-small-device">
                    <div class="col-3 col-lg-1 col-md-2">
                        Notes:
                    </div>
                    <div class="col-9 col-lg-11 col-md-10 text-dark">
                        ${order_data.order_detail.notes}
                    </div>
                </div>
    `

    for (let i = 0; i < cart_items.length; i++) {
        let item = cart_items[i];
        let food_img = item.food_image;
        if (window.location.href.includes("https://")) {
            food_img = food_img.replace("http://", "https://");
        }
        let item_row = `
                        <div class="row mb-2 order-item order-item-small-device">
                            <div class="col-3 col-lg-1 col-md-2">
                               <img class="food-item" src="${food_img}" />
                              
                            </div>
                            <div class="col-9 col-lg-11 col-md-10">    
                                <div class="row">            
                                    <div class="col-7">
                                        <h6 class="d-flex align-items-center">
                                            <span class="item-name">${item.name}</span>
                                        </h6>
                                    </div>
                                    <div class="col-5 text-end">
                                        <h6 class="price"><span class="me-1-cust">₹</span>${item.price}</h6>
                                        <span class="item-id d-none">${item.id}</span>
                                    </div> 
                                    <div class="col-12 m-0 align-items-left"> 
                                        <span class="text-muted" style="font-size: 0.85rem;">
                                        Price: <span class="text-dark fw-bold"> ₹ ${item['item-price']} </span>
                                        </span>
                                        <span class="text-muted ps-3" style="font-size: 0.85rem;">
                                            <span class="ps-2 pe-2"> | </span>Quantity: <span class="text-dark fw-bold item-qty"> ${item.quantity}</span>
                                        </span>
                                    </div>
                                    <div class="col-12 my-2 align-items-left"> 
                                        <span class="text-muted" style="font-size: 0.85rem;">
                                        Description: <span class="text-dark fw-bold">${item.description}</span>
                                        </span>
                                    </div>
                                <div>
                            <div>
                        </div>
                       
        `
        document.getElementById('order-items').innerHTML += item_row;
    }
    // ADDING TOTAL SECTION
    document.getElementById('order-items').innerHTML += `
                        <div class="d-flex justify-content-between mt-3">
                            <p class="text-muted">Sub Total</p>
                            <h6 class="total-amount"><span class="me-1-cust">₹</span><span
                                    id="sub-amount">${order_data.order_amount}</span></h6>
                        </div>
                        <div id="all-tax-area">
                        ${all_tax_area_html}
                        </div>
                        <div class="d-flex justify-content-between">
                            <p class="text-muted">Total</p>
                            <h6 class="total-amount"><span class="me-1-cust">₹</span><span class="amount-with-tax">

                                </span>
                            </h6>
                        </div>
                        
    `
}


async function openOrderProfile(order_id, page) {
    let order_data_url = "";

    if (page === "order-page") {
        order_data_url = `/theatre/api/order-data/${order_id}`
    }
    else {
        order_data_url = `/theatre/api/seat-last-order/${order_id}`
    }
    let order_data = await getRequest(order_data_url)
    document.getElementById('order-tab').click();
    order_id = order_data.order_detail.order_id;
    document.getElementById('bill-button').setAttribute('order_id', order_id);
    document.getElementById('kot-button').setAttribute('order_id', order_id);
    // creating order tab
    createOrderTab(order_data);
    // creating Cart Tab
    createCartTab(order_data);

    // refund form
    document.getElementById('refudn-form').setAttribute('action', `/theatre/refund-order/${order_id}`)

    // show tax
    showTax()

}

async function deliverOrder() {
    let order_deliver_button = document.getElementById('order-deliver-button');
    let order_id = order_deliver_button.getAttribute('order-id')

    let url = `/theatre/api/deliver-order/${order_id}`
    let order_status = await getRequest(url)


    if (order_status.message === 'Order Delivered Successfully') {
        document.getElementById('delivery-status').innerHTML = `<i class="fa fas fa-check-circle text-success mb-0 me-1"></i> Order Delivered`
    }

    document.getElementById('order-deliver-button').style.display = 'none'

    if (window.location.href.includes('theatre/all-seats')) {
        $("#orderPopUp").modal('hide');
    }

    else if (window.location.href.includes('theatre/live-orders')) {
        $("#orderPopUp").modal('hide');
    }
}

async function getPhonNumberByOrderId(id) {
    let api_url = `/theatre/api/get-phone-number-by-order-id/${id}`;
    let data = await getRequest(api_url);

    if (data.status == false) {
        showToast('bg-danger', "User Hasn't Provided There Phone Number Yet !");
    }

    let phone_number = data['phone_number'];
    document.getElementById('phone-number').innerText = phone_number;
}

async function UpdateSeatView(element) {
    let seen_status = document.getElementById('order-shown');
    if (seen_status.innerText.includes('Not Seen')) {
        if (window.location.href.includes('admin-portal')) {
            console.log('admin portal')
        }
        else {
            seat_id = element.getAttribute('seat-id');
            let url = `/theatre/api/is-order-viewed/${seat_id}`
            let data = await getRequest(url);

            seat = document.getElementById(`seat-${seat_id}`);

            if (seat !== null) {
                seat.setAttribute('class', 'seat seen');
            }


            seen_status.innerHTML = `Order Seen`;
        }
    }

}

const itemsTab = document.getElementById('items-tab');
document.querySelector('#items-tab').addEventListener('shown.bs.tab', function (event) {
    UpdateSeatView(itemsTab);
});


async function generateOTP(status) {
    const orderId = document.getElementById('order-id').innerText.replace('#', '');
    let optUrl = `/theatre/api/generate-otp/${orderId}/${status}`

    response = await getRequest(optUrl);

    if (response.status == 'sent') {
        showToast('bg-success', response.message);
    }
    else if (response.status == 'error') {
        showToast('bg-danger', response.message);
    }

}

const refundButton = document.getElementById('refund-button');
const regenerateOtp = document.getElementById('resend-otp-button');

regenerateOtp.addEventListener('click', async function () {
    await generateOTP("resend");
});

refundButton.addEventListener('click', async function () {
    await generateOTP("first");
});

const partialRefundBtn = document.getElementById('partial-refund-button')
partialRefundBtn.addEventListener('click', () => {
    const ul = document.getElementById('refunded-item-list');
    ul.innerHTML = "";

    // GET THE ORDER ITEMS
    const orderItems = document.getElementById('order-items');
    const all_food_images = orderItems.getElementsByClassName('food-item')

    for (let i = 0; i < all_food_images.length; i++) {
        const img = all_food_images[i]

        const itemDetail = img.parentElement.parentElement;
        const itemName = itemDetail.getElementsByClassName('item-name')[0].innerText;
        const itemQty = parseInt(itemDetail.getElementsByClassName('item-qty')[0].innerText);
        const item_id = itemDetail.getElementsByClassName('item-id')[0].innerText

        const li = document.createElement('li');
        li.setAttribute('class', 'list-group-item');
        li.innerHTML = `
        <div class="row">
            <div class="col-2">
                <input class="form-check-input me-1" type="checkbox" value="" aria-label="...">
            </div>
            <div class="col-5 text-start">
                ${itemName}
            </div>
            <span class="item-id d-none">
                ${item_id}
            </span>

            <div class="col-5 text-end">
                <div class="quantity">
                    <button class="btn btn-primary decrese-btn">-</button>
                    <input type="number" class="quantity-box" value="${itemQty}" readonly="" />
                    <button class="btn btn-primary increse-btn">+</button>
                </div>
            </div>
        
        </div>
        `
        const increseButton = li.getElementsByClassName('increse-btn')[0]
        increseButton.addEventListener('click', () => {
            IncreseQty(itemQty, increseButton)
        })

        const decreseButton = li.getElementsByClassName('decrese-btn')[0]
        decreseButton.addEventListener('click', () => {
            decreseQty(decreseButton);
        })
        ul.appendChild(li);
    }

    $("#refund-items").modal('show');
})

function IncreseQty(maxQty, btn) {
    if (!is_checked(btn)) {
        alert('Please first check the item CheckBox')
        return
    }
    const parentElement = btn.parentElement;
    const quantityInput = parentElement.getElementsByClassName('quantity-box')[0];

    var quantity = parseInt(quantityInput.value);
    quantity += 1;

    if (quantity > maxQty) {
        alert(`Customer has order only ${maxQty} item you can't exceed it`)
    }
    else {
        quantityInput.setAttribute('value', quantity);
    }
}

function decreseQty(btn) {
    if (!is_checked(btn)) {
        alert('Please first check the item CheckBox')
        return
    }
    const parentElement = btn.parentElement;
    const quantityInput = parentElement.getElementsByClassName('quantity-box')[0];

    var quantity = parseInt(quantityInput.value);

    quantity -= 1;
    if (quantity <= 0) {
        alert(`Quantity can never be 0`)
    }
    else {
        quantityInput.setAttribute('value', quantity)
    }
}

function is_checked(btn) {
    const dt = btn.parentElement.parentElement.parentElement
    return dt.getElementsByTagName('input')[0].checked
}


async function getRefund() {
    // generate the OTP
    await generateOTP("resend");
    
    
    // change the form url
    const orderId = document.getElementById('order-id').innerText.replace('#', '');
    document.getElementById('refudn-form').setAttribute('action', `/theatre/partial-refund-order/${orderId}`)
    
    // make the updated data in the field
    var refundData = []
    
    const ul = document.getElementById('refunded-item-list');
    
    const lis = ul.getElementsByTagName('li');
    
    for (let i = 0; i < lis.length; i++) {
        const li = lis[i]
        const item_id = parseInt(li.getElementsByClassName('item-id')[0].innerText);
        const item_qty = parseInt(li.getElementsByClassName('quantity-box')[0].value);
        
        const checkBox = li.getElementsByTagName('input')[0];
        
        if (checkBox.checked) {
            let append_data = {
                "id": item_id,
                "quantity": item_qty
            }
            refundData.push(append_data);
        }
    }
    
    const refindItemInput = document.getElementById('items-to-refund');
    refindItemInput.value = ""
    refindItemInput.value = JSON.stringify(refundData);
    
    // SHOW THE REFUND OTP POPUP
    $("#refund-order").modal('show');
    
    
}

const refundOtpPopupBtn = document.getElementById('partial-refund-btn-otp-popup');

refundOtpPopupBtn.addEventListener('click', async ()=> {
    await getRefund()
})