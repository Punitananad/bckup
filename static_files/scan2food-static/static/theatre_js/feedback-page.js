const CSRF_TOKEN = document.getElementsByName('csrfmiddlewaretoken')[0].value;

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

// Star rating interactions
const stars = Array.from(document.querySelectorAll('.star'));
let rating = 0;
stars.forEach((s, idx) => {
    s.addEventListener('click', () => { rating = idx + 1; stars.forEach((k, i) => k.classList.toggle('active', i < rating)); });
    s.addEventListener('mouseenter', () => { const i = stars.indexOf(s); stars.forEach((k, ix) => k.classList.toggle('active', ix <= i)); });
    s.addEventListener('mouseleave', () => { stars.forEach((k, i) => k.classList.toggle('active', i < rating)); });
});
document.getElementById('submit').addEventListener('click', async () => {
    const c = document.getElementById('comment').value.trim();
    document.getElementById('msg').style.display = 'block';

    if (rating == 0 && c.replaceAll(' ', '') === '') {
        document.getElementById('msg').innerText = 'Plese Gave some rattig or Write a comment !'
        setTimeout(() => { document.getElementById('msg').style.display = 'none'; }, 1000);
    }

    else {
        const rattingData = {
            ratting: rating,
            comment: c
        }

        const current_url = window.location.href;

        const data = await PostRequest(current_url, rattingData);

        if (data.status === 'done') {
            document.getElementById('comment').setAttribute('readonly', 'readonly');

            document.getElementById('msg').innerText = 'Thanks for your feedback! ⭐';

            setTimeout(() => {
                document.getElementById('msg').style.display = 'none';
                window.location.reload()
            }, 5000);
        }
    }

});


function LoadButtons() {
    const buttonArea = document.getElementById('button-area');
    buttonArea.innerHTML = '';

    const par = document.createElement('p')
    par.setAttribute('class', 'refund-copy mt-1')
    par.innerText = ""
    buttonArea.appendChild(par);

    const phoneNumber = JSON.parse(document.getElementById('query-number').textContent)

    const call_button = document.createElement('a');
    call_button.setAttribute('href', `tel:${phoneNumber}`);
    call_button.setAttribute('class', 'refund-button mx-1 my-1');
    call_button.innerHTML = '<i class="fas fa-phone-alt"></i> Call Manager';
    buttonArea.appendChild(call_button);

    const whatsappButton = document.createElement('a');
    whatsappButton.setAttribute('href', 'https://wa.me/+918708999872');
    whatsappButton.setAttribute('target', '_blank');
    whatsappButton.setAttribute('class', 'refund-button mx-1 my-1');
    whatsappButton.innerHTML = '<i class="fab fa-whatsapp"></i> Start Chat';
    buttonArea.appendChild(whatsappButton);

    const mailButton = document.createElement('a');
    mailButton.setAttribute('href', 'mailto:support@scan2food.com');
    mailButton.setAttribute('class', 'refund-button mx-1 my-1');
    mailButton.setAttribute('target', '_blank');
    mailButton.innerHTML = '<i class="far fa-envelope"></i> Send Mail';
    buttonArea.appendChild(mailButton);

    const downloadPermission = JSON.parse(document.getElementById('download_invoice').innerText);

    if (downloadPermission === true) {
        const order_id = JSON.parse(document.getElementById('order-id').innerText)
        const downloadInvoice = document.createElement('a');
        downloadInvoice.setAttribute('href', `/theatre/invoice/${order_id}`);
        downloadInvoice.setAttribute('class', 'refund-button mx-1 my-1');
        downloadInvoice.setAttribute('target', '_blank');
        downloadInvoice.innerHTML = '<i class="fa fa-download"></i> Invoice';
        buttonArea.appendChild(downloadInvoice);
    }

}

LoadButtons();


