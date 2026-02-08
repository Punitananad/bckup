// Generalized radial countdown
function startCountdown(targetTimeStr, countdownMinutes = 30) {
    // Parse given target time string
    const targetTime = new Date(targetTimeStr);

    // Calculate when countdown should end
    const endTime = new Date(targetTime.getTime() + countdownMinutes * 60 * 1000);

    // Current time
    let now = new Date();

    // If the countdown already ended, trigger immediately
    if (now >= endTime) {
        timeup();
        return;
    }

    // Total seconds for this countdown
    let total2 = Math.floor((endTime - targetTime) / 1000);
    let remain2 = Math.floor((endTime - now) / 1000);

    const eta2b = document.getElementById('eta2b');
    const pg2 = document.getElementById('pg2');
    const C2 = 2 * Math.PI * 52;

    function fmt2(s) {
        const m = Math.floor(s / 60).toString().padStart(2, '0');
        const x = (s % 60).toString().padStart(2, '0');
        return m + ':' + x;
    }

    function tick2() {
        eta2b.textContent = fmt2(remain2);
        const ratio = 1 - (remain2 / total2);
        pg2.setAttribute('stroke-dasharray', C2);
        pg2.setAttribute('stroke-dashoffset', (ratio * C2).toFixed(2));
        if (remain2 <= 0) {
            eta2b.textContent = 'Time Up';
            pg2.setAttribute('stroke', 'var(--orange)');
            clearInterval(t2);
            timeup();
        }
        remain2--;
    }

    const t2 = setInterval(tick2, 1000);
    tick2();
}

// --- Refund + Timeup handlers ---
const refundBtn = document.getElementById('claimRefund');
function showRefund() {
    if (!refundBtn) return;
    refundBtn.classList.remove('hidden');
    refundBtn.setAttribute('aria-hidden', 'false');
}

function timeup() {
    // whatever you want when time ends
    showRefund(); // or remove if you don't want refund button here
    document.getElementById('eta2b').parentElement.innerHTML = `
    <svg class="clock clock--small" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <circle cx="12" cy="12" r="9" fill="none" stroke="var(--blue)" stroke-width="2" />
        <line x1="12" y1="12" x2="12" y2="6" stroke="var(--orange)" stroke-width="2" stroke-linecap="round" />
        <line x1="12" y1="12" x2="17" y2="12" stroke="var(--blue)" stroke-width="2" stroke-linecap="round" />
    </svg>
    Time Up !
    `

    const refreshButton = document.getElementById('refresh-button');
    refreshButton.remove();

    const buttonArea = document.getElementById('button-area');
    buttonArea.innerHTML = '';

    const par = document.createElement('p')
    par.setAttribute('class', 'refund-copy mb-2')
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

    const refundButton = document.createElement('a');
    refundButton.setAttribute('class', 'refund-button mx-1 my-1');
    refundButton.innerHTML = '<i class="fas fa-wallet"></i> Raise Refund Request';
    refundButton.addEventListener('click', () => {
        openModal()
    })
    buttonArea.appendChild(refundButton);

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




// Function to open the modal
function openModal() {
    document.getElementById('customModal').style.display = 'flex';
}

// Function to close the modal
function closeModal() {
    document.getElementById('customModal').style.display = 'none';
}

// Example submit function
function submitPhone() {
    var customerMobileNumber = JSON.parse(document.getElementById('customer-mobile-number').innerText)
    if (customerMobileNumber.includes("+")) {
        customerMobileNumber = customerMobileNumber.replaceAll("+91", "")
    }
    else {
        if (customerMobileNumber.length > 10) {
            if (customerMobileNumber.slice(0, 2) == "91") {
                customerMobileNumber = customerMobileNumber.slice(2, -1)
            }
        }
    }


    const phone = document.getElementById('phone-number').value;

    if (phone === customerMobileNumber) {
        const form = document.getElementById('phone-number-form')
        form.submit()
    }
    else {
        showToast('Please enter the correct mobile number which you have given at time of order');
    }

    closeModal();
}

closeModal()

// Ensure toast container exists
let toastContainer = document.getElementById('toast-container');
if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    document.body.appendChild(toastContainer);
}

// Toast function
function showToast(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toastContainer.appendChild(toast);

    // Trigger show animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 50);

    // Remove toast after specified duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}
