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

    try {

        if (order_data.order_detail.food_delivered === false) {
            document.getElementById('delivery-status').innerHTML = `<i class="fa fas fa-clock text-danger mb-0 me-1"></i>Delivery Pending`;
            document.getElementById('order-deliver-button').setAttribute('style', '');
            document.getElementById('delivery-detail-box').setAttribute('class', 'd-none');
        }
        else {
            document.getElementById('delivery-status').innerHTML = `<i class="fa fas fa-check-circle text-success mb-0 me-1"></i> Order Delivered`;
            document.getElementById('order-deliver-button').style.display = 'none';
            document.getElementById('delivery-detail-box').setAttribute('class', 'd-flex justify-content-between');
            document.getElementById('delivery-detail-box-value').innerText = order_data.order_detail.delivery_time;
        }
    }
    catch (error) {

    }

    document.getElementById('order-deliver-button').setAttribute('order-id', order_data.order_detail.order_id)

    document.getElementById('order-id').innerText = `#${order_data.order_detail.order_id}`;
    document.getElementById('seat-name').innerText = order_data.seat;

    document.getElementById('theatre-name').innerText = order_data.theatre_name;

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

        try {
            if (order_data.order_detail.payment_method == 'Gateway') {
                document.getElementById('gateway-detail').classList.remove('d-none');
                document.getElementById('gateway-name').innerText = order_data.order_detail.payment_gateway;

                document.getElementById('gateway-transaction').classList.remove('d-none');
                document.getElementById('gateway-transaction-id').innerText = order_data.order_detail.gateway_order_id;
            }
        }

        catch (error) {
            console.log('Error in payment gateway details');
        }
    }

    if (order_data.order_detail.is_shown == true) {
        document.getElementById('order-shown').innerHTML = `Order Seen`;
    }
    else {
        document.getElementById('order-shown').innerHTML = `Order Not Seen Yet !`;
    }

    document.getElementById('payment-status').innerHTML = payment_status;
    document.getElementById('payment-tab-payment-status').innerHTML = payment_status;

    document.getElementById('scan2food-payment-id-detail').setAttribute('class', 'd-flex justify-content-between');
    document.getElementById('scan2food-payment-id-value').innerText = order_data.order_detail.payment_id;

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
        let item_row = `
                    <div class="row mb-2 order-item order-item-small-device">
                        <div class="col-3 col-lg-1 col-md-2">
                            <img class="food-item" src="${item.food_image}" />
                        </div>  
                        <div class="col-9 col-lg-11 col-md-10">    
                            <div class="row">            
                                <div class="col-7">
                                    <h6 class="d-flex align-items-center">
                                        <span class="">${item.name}</span>
                                    </h6>
                                </div>
                            <div class="col-5 text-end">
                                <h6 class="price"><span class="me-1-cust">₹</span>${item.price}</h6>
                            </div> 
                            <div class="col-12 m-0 align-items-left"> 
                                <span class="text-muted" style="font-size: 0.85rem;">
                                    Price: <span class="text-dark fw-bold"> ₹ ${item['item-price']} </span>
                                </span>
                                <span class="text-muted ps-3" style="font-size: 0.85rem;">
                                    <span class="ps-2 pe-2"> | </span>
                                    Quantity: <span class="text-dark fw-bold"> ${item.quantity}</span>
                                </span>
                            </div>
                            <div class="col-12 my-2 align-items-left"> 
                                <span class="text-muted" style="font-size: 0.85rem;">
                                Description: <span class="text-dark fw-bold">${item.description}</span>
                                </span>
                            </div>
                        </div>
                       
        `
        document.getElementById('order-items').innerHTML += item_row;
    }
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


async function openOrderProfile(order_id) {
    let order_data_url = "";


    order_data_url = `/theatre/api/order-data/${order_id}`

    let order_data = await getRequest(order_data_url)
    document.getElementById('order-tab').click();
    order_id = order_data.order_detail.order_id;
    document.getElementById('bill-button').setAttribute('order_id', order_id);
    document.getElementById('kot-button').setAttribute('order_id', order_id);
    // creating order tab
    createOrderTab(order_data);
    // creating Cart Tab
    createCartTab(order_data);

    // show tax
    showTax()

}

async function deliverOrder() {

    let url = `/theatre/api/deliver-order/${order_id}`
    let order_status = await getRequest(url)


    if (order_status.message === 'Order Delivered Successfully') {
        document.getElementById('delivery-status').innerHTML = `<i class="fa fas fa-check-circle text-success mb-0 me-1"></i> Order Delivered`
    }


    if (window.location.href.includes('theatre/all-seats')) {
        $("#orderPopUp").modal('hide');
    }

    else if (window.location.href.includes('live-orders')) {
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
        if (!window.location.href.includes('admin-portal')) {

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