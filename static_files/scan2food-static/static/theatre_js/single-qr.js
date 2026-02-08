// GET THE CSRF TOKEN FOR PROTECTION
const CSRF_TOKEN = document.getElementsByName('csrf-token')[0].content;

const selected_hall = document.getElementById('selected-hall');
const selected_row = document.getElementById('selected-row');
const selected_seat_input = document.getElementById('selected-seat');
const suggestions = document.getElementById("suggestions");
// Ensure 'show' class is removed by default
suggestions.classList.remove('show');


var THEATRE_DATA;
var SEATING_DATA = {};

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

function loadRowAndSeat(hall_name) {
    const hall_data = SEATING_DATA[hall_name];
    selected_row.innerHTML = ""
    selected_row.innerHTML = `<option value="">Select Row</option>`
    for (let i in hall_data) {
        selected_row.innerHTML += `<option value="${i}">${i}</option>`
    }
    selected_row.value = "";
}

function loadSeats(seats) {
    selected_seat_input.innerHTML = '<option vlaue="">Select Seat</option>'
    
    for (let i in seats) {
        selected_seat_input.innerHTML += `<option value="${seats[i].seat_id}">${seats[i].seat_name}</option>`
    }
}

function CreateHalls(seating) {
    const hall_box = document.getElementById('hall-box');

    SEATING_DATA = seating;

    for (let hall in seating) {

        // CREATE THE MAIN DIV
        const colDiv = document.createElement('div');
        colDiv.setAttribute('class', 'col-xl-3 col-lg-4 col-sm-6 col-6 my-2')

        // CREATE THE CARD INSIDE THE MAIN DIV
        const card = document.createElement('div');
        // ADD CLASS TO CARD
        card.setAttribute('class', 'card shadow-lg border-0 cursor-pointer');
        // add styling
        card.setAttribute('style', 'border-radius: 1rem; overflow: hidden;')

        // SET INNEER HTML OF THE CARD
        card.innerHTML = `
                <div class="d-flex justify-content-center align-items-center bg-light" style="height: 180px;">
                    <div class="rounded-circle d-flex justify-content-center align-items-center" style="width: 100px; height: 100px; background: linear-gradient(135deg, #fda016, #feaa2d); color: white; font-size: 1.5rem; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                        ${hall}
                    </div>
                </div>
                <div class="card-body text-center">
                    <p class="card-text text-dark fw-bold">
                        ${hall}
                    </p>
                </div>
        `

        card.addEventListener('click', () => {
            // SET THE SEATING PLAN ACCORDING TO THE HALL
            selected_hall.value = hall;

            // Load All The Rows and Seats
            loadRowAndSeat(hall)
            selected_seat_input.value = "";
            document.getElementById("suggestions").innerText = "";
            // OPEN THE POPUP
            $("#seat-modal").modal('show')
        })
        colDiv.appendChild(card);

        hall_box.appendChild(colDiv);

        // CREATE A SELECT IN THE SELECTED FORM
        const option = document.createElement('option');
        option.value = hall;
        option.innerText = hall;

        selected_hall.appendChild(option);

    }

}

async function loadData() {
    const theatre_id = document.getElementById('theatre-id').innerText;
    const url = `/theatre/api/theatre-detail`;
    const data = { 'theatre_id': theatre_id };
    const response = await PostRequest(url, data);

    // UPDATE THE THEATRE DATA
    THEATRE_DATA = response;

    const theatre_name = response.theatre_name;

    const theatre_name_label = document.getElementById('theatre-name-label')
    theatre_name_label.innerText = theatre_name

    // CREATE THE HALLS
    const seating = response.seating;
    CreateHalls(seating);
}

selected_row.addEventListener('change', function (event) {
    const hall_name = selected_hall.value;
    const row_name = event.target.value;

    selected_seat_input.value = "";

    if (row_name === "") {
        selected_seat_input.setAttribute('readonly', '');
    }
    else {
        try {
            selected_seat_input.removeAttribute('readonly');
        }
        catch (error) {
            console.log(error);
        }
    }

    const all_seats = SEATING_DATA[hall_name][row_name]

    loadSeats(all_seats);
})

window.onload = async () => {
    await loadData();
}


// OPEN MENU BUTTON
const menuBtn = document.getElementById('open-menu-button');

menuBtn.addEventListener('click', () => {
    let seat_id = selected_seat_input.value;

    if (seat_id === "") {
        alert('Please enter valid seat number');
    }

    else {
        const menu_url = `/theatre/show-menu/${seat_id}`
        window.open(menu_url, '_self');
    }
})
