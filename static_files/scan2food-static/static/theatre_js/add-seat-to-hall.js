const Alphabets = ['A', "B", 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

let lastAlphabetSelect = document.getElementById('last-alphabet')
for (let i = 0; i < Alphabets.length; i++) {
    let option = document.createElement('option');
    option.value = Alphabets[i]
    option.innerText = Alphabets[i]
    lastAlphabetSelect.appendChild(option);
}


// function to create new rows and seats
function createRow(btn, alphabet, seatCounts) {
    let allHallList = document.getElementById('all-hall-list');
    let div;
    if (btn === "") {
        div = document.createElement('div');
        div.setAttribute('class', 'row custom-theatre-row');

    }

    else {
        div = btn.parentElement;
    }

    let smallDiv = document.createElement('div');
    smallDiv.setAttribute('class', 'label row-label')

    smallDiv.innerText = alphabet;

    div.appendChild(smallDiv);
    allHallList.appendChild(div);
// yaha bhi seats ko ek div meh wrap karna HTMLDetailsElement, <div class="seat-wrapper"></div>
    // creating the seats 
    for (let i = 0; i < seatCounts; i++) {
        let newDiv = document.createElement('div');
        newDiv.setAttribute('class', 'seat');
        newDiv.innerText = `${alphabet}${i + 1}`
        div.appendChild(newDiv);
    }

    let addSeatButton = document.createElement('button');
    addSeatButton.setAttribute('class', 'seat bg-success text-white');
    addSeatButton.innerText = "+"

    addSeatButton.setAttribute('onclick', 'addSeat(this)')

    div.appendChild(addSeatButton);

    let RemoveSeatButton = document.createElement('button');
    RemoveSeatButton.setAttribute('class', 'seat btn-danger text-white');
    RemoveSeatButton.innerText = "-"

    RemoveSeatButton.setAttribute('onclick', 'removeSeat(this)');

    div.appendChild(RemoveSeatButton);

}

let addRowButton = document.getElementById('add-rows')
addRowButton.addEventListener('click', () => {
    // Empty the Entire Section
    let allHallList = document.getElementById('all-hall-list');
    allHallList.innerHTML = "";

    let last_value = document.getElementById('last-alphabet').value;

    for (let i = 0; i < Alphabets.length; i++) {
        let alphabet = Alphabets[i];

        let row = document.createElement('div');
        row.setAttribute('class', 'row custom-theatre-row');

        let row_head = document.createElement('div');
        row_head.innerText = alphabet;
        row_head.setAttribute('class', 'label row-label');

        row.appendChild(row_head);

        // creating input
        let seatInput = document.createElement('input');
        seatInput.setAttribute('type', 'number')
        seatInput.setAttribute('class', 'form-control');
        seatInput.setAttribute('style', 'width: 15vw; margin: 0.5%')

        row.appendChild(seatInput);

        // creating Button
        let button = document.createElement('button');
        button.setAttribute('class', 'btn btn-success text-white');
        button.innerText = 'Add Row'
        button.setAttribute('style', 'width:15vw; margin: 0.5%;')

        // button functionality
        button.addEventListener('click', () => {
            let seatCounts = seatInput.value;

            // run to add new row
            createRow(button, alphabet, seatCounts);

            seatInput.remove();
            button.remove();
            row_head.remove();
        })
        row.appendChild(button);

        // append the complete row with input and button
        allHallList.appendChild(row);


        if (alphabet === last_value) {
            break;
        }

        else {
            continue;
        }
    }

    let ls_al = document.getElementById('last-alphabet');
    let parent = ls_al.parentElement;

    let value = ls_al.value;
    ls_al.remove()

    let new_input = document.createElement('input');
    new_input.setAttribute('class', 'form-control');
    new_input.setAttribute('name', 'last-alphabet');
    new_input.setAttribute('id', 'last-alphabet');
    new_input.value = value;
    new_input.removeAttribute('readonly', '');

    parent.appendChild(new_input);



    addRowButton.remove()
})


function saveSeats() {
    let return_data = {}
    let allRow = document.getElementsByClassName('custom-theatre-row');
    for (let i = 0; i < allRow.length; i++) {
        let row = allRow[i];
        let label = row.getElementsByClassName('label')[0].innerText;
        let append_data = [];
        let allSeats = row.getElementsByClassName('seat');
        for (let n = 0; n < allSeats.length; n++) {
            let seat = allSeats[n];
            if (seat.innerText == "+" || seat.innerText == "-") {
                console.log('')
            }
            else {
                append_data.push(seat.innerText);
            }
        }
        return_data[label] = append_data;
    }
    return JSON.stringify(return_data);
}


document.getElementById('update-button').addEventListener('click', () => {
    let send_data = saveSeats()
    document.getElementById('send-data').value = send_data;
    document.getElementById('main-submit').click();
})

function removeSeat(button) {

    let row = button.parentElement;
    let all_seats = row.getElementsByClassName('seat');

    let seat_length = all_seats.length - 3;

    // get the seat going to remove.
    let last_seat = all_seats[seat_length]
    last_seat.remove();

}

function addSeat(button) {
    let row = button.parentElement;
    let label = row.getElementsByClassName('label')[0].innerText
    let all_seats = row.getElementsByClassName('seat');

    let new_seat = document.createElement('div');
    new_seat.setAttribute('class', 'seat')

    let seat_number;
    if (all_seats.length <= 2) {
        seat_number = 1;
        new_seat.innerText = `${label}${seat_number}`
    }
    else {
        seat_number = all_seats.length - 1
        new_seat.innerText = `${label}${seat_number}`
    }

    // get the add and remove button
    let addButton = all_seats[all_seats.length - 1];
    let addButton_html = addButton.outerHTML;
    let removeButton = all_seats[all_seats.length - 2]
    let removeButton_html = removeButton.outerHTML;

    // remove the add and remove buttons
    addButton.remove()
    removeButton.remove()

    row.appendChild(new_seat);

    // // add new add and remove button on web application
    row.innerHTML += removeButton_html + addButton_html

}