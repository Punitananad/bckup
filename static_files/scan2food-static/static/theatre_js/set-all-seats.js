const hall_name = JSON.parse(document.getElementById('hall-name').innerText)

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

function SetUpHall(seating_plan) {
    let hall_seats = seating_plan[hall_name];

    for (let row in hall_seats) {
        let row_count = hall_seats[row].length;
        createRow("", row, row_count);

        if (Object.keys(hall_seats)[Object.keys(hall_seats).length - 1] == row) {
            document.getElementById('last-alphabet').value = row;
        }
    }

    if (Object.keys(hall_seats).length !== 0) {

        setTimeout(() => {
            document.getElementById('add-rows').remove();

        }, 1000);
    }
}

async function ShowSeats() {
    SeatingPlan = await getRequest('/theatre/api/all-seating-plan');
    console.log(SeatingPlan);

    SetUpHall(SeatingPlan)
}

ShowSeats()
