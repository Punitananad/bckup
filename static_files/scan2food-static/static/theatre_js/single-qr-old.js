// GET THE CSRF TOKEN FOR PROTECTION
const CSRF_TOKEN = document.getElementsByName('csrf-token')[0].content;

const selected_hall = document.getElementById('selected-hall');
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

function CreateHalls(seating) {
    const hall_box = document.getElementById('hall-box');


    for (let hall in seating) {
        SEATING_DATA[hall] = [];
        // ADD ALLTHE SEATS IN SEATING DATA LIST
        const row = seating[hall]

        for (let i in row) {
            for (let seat_indx in row[i]) {
                const seat = row[i][seat_indx]
                const seat_name = seat.seat_name;

                // APPEND THE SEAT NAME INTO THE SEATING DATA
                SEATING_DATA[hall].push(seat_name);
            }
        }

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

selected_seat_input.addEventListener('input', function () {
    const hall_name = selected_hall.value;
    const query = this.value.toLowerCase();
    suggestions.innerHTML = ""; // clear previous
    if (query.length === 0) {
        suggestions.classList.remove("show"); // Hide ul if input is empty
        return;
    }

    const filtered = SEATING_DATA[hall_name].filter(item => item.toLowerCase().includes(query));

    filtered.forEach(item => {
        const li = document.createElement("li");
        li.innerHTML = `<a class="dropdown-item" href="#">${item}</a>`;
        li.addEventListener("click", function (e) {
            e.preventDefault();
            selected_seat_input.value = item;
            suggestions.innerHTML = "";
            suggestions.classList.remove("show"); // Hide suggestions after selection
        });
        suggestions.appendChild(li);
    });

    if (filtered.length > 0) {
        suggestions.classList.add("show");
    } else {
        suggestions.classList.remove("show"); // Hide ul if no children
        suggestions.innerHTML = ""; // Ensure it's empty
    }
})

window.onload = async () => {
    await loadData();
}


// OPEN MENU BUTTON
const menuBtn = document.getElementById('open-menu-button');

menuBtn.addEventListener('click', () => {
    const hall_name = selected_hall.value;
    const selected_seat = selected_seat_input.value;

    const selected_seat_name = selected_seat.toUpperCase();

    // FIND THE SEAT ID OF THE SEAT
    const hall_seats = THEATRE_DATA['seating'][hall_name];
    let seat_id = "";

    for (let i in hall_seats) {
        const row = hall_seats[i];
        const first_seat = row[0].seat_name;

        // CHECK IF THE FIRST SEAT SEAT NAME INCLUDES THE SELECTED SEAT OR OR
        if (first_seat.includes(selected_seat[0])) {
            // HERE SEAT IS MATCHING WITH THE ROW
            // RUN A FOR LOOP AND CHECKS WHETHER AND GET THE SEAT ID
            for (let seat_indx in hall_seats[i]) {
                const seat = hall_seats[i][seat_indx]
                if (seat.seat_name == selected_seat_name) {
                    seat_id = seat.seat_id;
                    break;
                }
                else {
                    continue;
                }
            }
        }
    }

    if (seat_id === "") {
        alert('Please enter valid seat number');
    }
    
    else {
        const menu_url = `/theatre/show-menu/${seat_id}`
        window.open(menu_url, '_self');
    }
})
