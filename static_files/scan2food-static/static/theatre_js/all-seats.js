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

// function to create an simple Hall
function SetUpHall(seating_plan) {
    for (let hall in seating_plan) {
        let index = Object.keys(seating_plan).indexOf(hall)

        let hallList = document.getElementById('hall-list');

        let li = document.createElement('li');
        li.setAttribute('class', 'nav-item');

        let li_html = `
                <a class="d-flex align-items-center text-start mx-3 ms-0" data-bs-toggle="pill"
                    href="#tab${index}">
                    <div class="shadow p-3">
                        <h6 class="mt-n1 mb-0">${hall}</h6>
                        <p class="mb-0 text-muted">Order Recieved - <strong class="text-primary fw-bold order-received-label">0</strong>  </p>
                    </div>
                </a>
        `
        li.innerHTML = li_html;

        a_tag = li.getElementsByTagName('a')[0];
        if (index === 0) {
            a_tag.setAttribute('class', 'd-flex align-items-center text-start mx-3 ms-0 active')
        }
        let row = seating_plan[hall]

        // creating seats in hall
        SetUpSeats(row, index, hall)
        hallList.appendChild(li);
    }

    showOrderData()
}

var table_name = ""

function SetUpSeats(all_row, index, hall_name) {
    let allHallBox = document.getElementById('all-hall-box');
    let hall = document.createElement('div');
    if (index === 0) {
        hall.setAttribute('class', 'tab-pane fade show p-0 active seating-hall');
    }
    else {
        hall.setAttribute('class', 'tab-pane fade show p-0 seating-hall');
    }
    hall.setAttribute('id', `tab${index}`)

    allHallBox.appendChild(hall)

    // start creating theatre View
    for (let row in all_row) {
        let theatreRow = document.createElement('div');
        theatreRow.setAttribute('class', 'row custom-theatre-row');

        let label = document.createElement('div');
        label.setAttribute('class', 'row-label');

        label.innerText = row;

        // appending the label to the hall
        theatreRow.appendChild(label)

        // getting all the seats
        let all_seats = all_row[row]
        // Create a wrapper div for the seats
        let seatWrapper = document.createElement('div');
        seatWrapper.setAttribute('class', 'seat-wrapper');

        // theatreRow.appendChild(seatWrapper);

        // Kanika - 14 dec - is for loop se phle ek div or add kar dena <div class="seat-wrapper">
        // creating the seats and update on the row
        for (let i = 0; i < all_seats.length; i++) {
            let seat_data = all_seats[i];
            let seat = document.createElement('div');
            if (seat_data.is_vacent) {
                seat.setAttribute('class', 'seat');
            }
            else {
                if (seat_data.payment_method == 'Cash' && seat_data.payment_status == 'Created') {
                    seat.setAttribute('class', 'seat orderreceived')
                }
                else {
                    if (seat_data.is_shown === true) {
                        seat.setAttribute('class', 'seat seen')

                    }
                    else {
                        seat.setAttribute('class', 'seat paymentreceived')
                    }

                    
                }
            }
            seat.setAttribute('id', `seat-${seat_data.seat_id}`)
            seat.innerText = seat_data.seat_name

            // append seat to the theatre row
            theatreRow.appendChild(seat);

            let table_position = `${hall_name} | ${seat_data.seat_name}`
            seat.addEventListener('click', async () => {
                await OpenPopUp(table_position, seat);
            })
            table_name = table_position
        }

        hall.appendChild(theatreRow);
    }
}

var SeatingPlan = {}
async function ShowSeats() {
    SeatingPlan = await getRequest('/theatre/api/all-seating-plan');
    SetUpHall(SeatingPlan)
}

function showOrderData() {
    let totalOrders = 0
    let allHallBox = document.getElementById('all-hall-box');
    let allHalls = allHallBox.getElementsByClassName('seating-hall');
    let orderReceivedLabel = document.getElementsByClassName('order-received-label')

    for (let i = 0; i < allHalls.length; i++) {
        let hall = allHalls[i]
        let running_orders = hall.getElementsByClassName('paymentreceived').length + hall.getElementsByClassName('seen').length
        totalOrders += running_orders
        orderReceivedLabel[i].innerText = running_orders;
    }

    document.getElementById('total-pending-orders').innerText = totalOrders;
}

ShowSeats()

async function OpenPopUp(table_name, div = "") {
    let seat_class
    if (div === "") {
        seat_class = 'seat'
    }
    else {
        seat_class = div.getAttribute('class');
    }
    if (seat_class === 'seat') {
        document.getElementById('menuePopUpLabel').innerText = table_name
        let table_cart_data = localStorage.getItem(table_name);

        let cartBox = document.getElementById('cart-div');

        if (table_cart_data === null) {
            localStorage.setItem(table_name, JSON.stringify({}));
            document.getElementById('total-cart-amount').innerText = 0;
            document.getElementById('cart-amount').innerText = 0;
        }

        cartBox.setAttribute('selected-table-name', table_name);

        loadExistingCart(table_name);
        $("#menuePopUp").modal('show');
    }
    else if (seat_class === 'seat paymentreceived' || seat_class === 'seat seen') {
        let seat_id = div.getAttribute('id');
        seat_id = seat_id.split("-")[1];

        await openOrderProfile(seat_id, "last-seat");
        document.getElementById('orderPopUpLabel').innerText = table_name;

        $("#orderPopUp").modal('show');
    }
    else {
        let seat_id = div.getAttribute('id');
        seat_id = seat_id.replaceAll('seat-', '');
        let url = `/theatre/get-seat-last-order/${seat_id}`
        window.open(url, "", "width=600, height=600");
    }


}
