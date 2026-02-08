// GET THE CSRF TOKEN FOR PROTECTION
const CSRF_TOKEN = document.getElementsByName('csrf-token')[0].content;

const ROW_DROPDOWN = document.getElementById('selected-row');
const SEAT_DROPDOWN = document.getElementById('selected-seat');

var SEATING_DATA;

// function to hit the post request
async function PostRequest(url, data) {
    `Post Request funcition send POST Request to server and get the response from the url and send data in json format stored in data`
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

function updateRowDropDown() {
    `
    1/. Remove all the Rows from Select Row and add all rows of the hall dropdown
    2/ after appending all the seats add change event listener to the seat drowdown
    `
    ROW_DROPDOWN.innerHTML = '';
    let option = document.createElement('option');
    option.innerText = 'Select Row';
    option.value = "";
    ROW_DROPDOWN.appendChild(option)
    for (let row in SEATING_DATA) {
        option = document.createElement('option');
        option.value = row;
        option.innerText = row;
        ROW_DROPDOWN.appendChild(option)
    }

    // add event listener and update Seats
    ROW_DROPDOWN.addEventListener('change', (event) => {
        updateSeats(event.target.value);
    })
}

function updateSeats(row_name) {
    `
    1/. get the selected row
    2/. First Empty all the seats
    3/. On Behalf of Selected rows append all the seats
    `
    SEAT_DROPDOWN.innerHTML = ""
    let option = document.createElement('option');
    option.innerText = 'Select Row';
    option.value = "";
    SEAT_DROPDOWN.appendChild(option);

    const row_data = SEATING_DATA[row_name];

    for (let i in row_data) {
        const seat_data = row_data[i];
        option = document.createElement('option');
        option.innerText = seat_data.seat_name;
        option.value = seat_data.seat_id;
        SEAT_DROPDOWN.appendChild(option);
    }


}

async function loadData() {
    `get the data from server by sending the "theatre-id" from the api "/theatre/api/theatre-detail" `
    const theatre_id = document.getElementById('theatre-id').innerText;
    const url = `/theatre/api/theatre-detail`;
    const data = { 'theatre_id': theatre_id };
    const response = await PostRequest(url, data);

    const theatre_name = response.theatre_name;

    const theatre_name_label = document.getElementById('theatre-name-label')
    theatre_name_label.innerText = theatre_name

    // CREATE THE ROW AND SEAT DROPDOWN
    const seating = response.seating;
    const hall_name = JSON.parse(document.getElementById('hall-name').innerText)

    const hall_name_label = document.getElementById('hall-name-label')
    hall_name_label.innerText = hall_name;
    
    SEATING_DATA = seating[hall_name]
    updateRowDropDown()
}

window.onload = async () => {
    await loadData()
}


const OpenMenuBtn = document.getElementById('open-menu-button');

function submitForm() {
    const selected_seat_id = SEAT_DROPDOWN.value;
    
    if (selected_seat_id === "") {
        alert('Pleaes Select The right Seat');
    }
    else {
        window.open(`/theatre/show-menu/${selected_seat_id}`, '_self');
    }
}

OpenMenuBtn.addEventListener('click', submitForm)