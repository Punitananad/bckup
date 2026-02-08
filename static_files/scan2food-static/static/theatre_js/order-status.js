const customer_phone_number = JSON.parse(document.getElementById('customer-phone-number').textContent);

// function to hit the post request
async function PostRequest(url, data) {
    csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
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
            throw new Error('Failed to fetch data');
        });
}



function CheckPhoneNumber() {
    if (customer_phone_number.length === 0) {
        $("#detailBox").modal('show');
    }
    
}

async function updatePhoneNumber(phone_number) {
    let data = {'phone_number': phone_number}
    let url = window.location.href;
    let update_status = await PostRequest(url, data);
    return update_status;
}

function checkValidation() {
    let phone_number = document.getElementById('phone-number');
    if (phone_number.value.length === 10){
        phone_number.setAttribute('class', 'form-control is-valid');
        return true
    }
    else {
        phone_number.setAttribute('class', 'form-control is-invalid');
        return false
    }
}

async function submitForm() {
    let is_valid = checkValidation();
    if (is_valid === true) {
        phone_number = document.getElementById('phone-number').value;
        phone_status = await updatePhoneNumber(phone_number);
        setTimeout(() => {
            $("#detailBox").modal('hide');
        }, 200);
    }
}

window.onload = function () {
    setTimeout(() => {
        CheckPhoneNumber()
    }, 100); // 2000 milisecond means 1 second
};