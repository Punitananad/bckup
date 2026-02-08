// function for get request
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


const selected_theatre_id = document.getElementById('selected-theatre-id').value;

// load all theatres
async function loadAllTheatres() {
    const all_theatre_url = `/theatre/api/get-all-theatres`
    all_theatres = await getRequest(all_theatre_url);
    all_theatres = all_theatres.all_theatres;

    const sel = document.getElementById('selected-theatre');
    // create the select in the order
    for (let i = 0; i < all_theatres.length; i++) {
        const theatre_detail = all_theatres[i];
        const opt = document.createElement('option');
        opt.setAttribute('value', theatre_detail.theatre_id);
        opt.innerText = theatre_detail.name
        sel.appendChild(opt);
    }

    sel.value = selected_theatre_id;

}

loadAllTheatres()


function makeWhatsappUrl() {
    whatsappNumbers = document.getElementsByClassName('whatsapp-numbers');
    for (let i = 0; i < whatsappNumbers.length; i++) {
        td = whatsappNumbers[i]
        phone_numbers = td.innerText.split(',');
        td.innerText = ""
        // run the loop 2 time and create the url for whatsapp reply message
        for (let num = 0; num < phone_numbers.length; num ++) {
            let a = document.createElement('a')
            a.innerText = `${phone_numbers[num]} , `
            a.href = `https://web.whatsapp.com/send?phone=${phone_numbers[num]}`
            a.target = "_blank"
            td.appendChild(a);
        }
    }
}

makeWhatsappUrl()