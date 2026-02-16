const all_canvas = document.getElementsByClassName('qr-code');
const protocol = window.location.protocol;
const host_name = window.location.host;

// Function to generate QR codes for each seat
function generateQRCode(id, url) {
    const qrCodeContainer = document.getElementById(id);

    // Check if element and URL are valid
    if (!qrCodeContainer) {
        console.error(`Element with ID '${id}' not found.`);
        return;
    }

    if (!url) {
        console.error('Invalid URL provided for QR code generation.');
        return;
    }

    QRCode.toCanvas(qrCodeContainer, url, function (error) {
        if (error) {
            console.error('QR Code generation error:', error);
        } else {
            console.log(`QR code generated for ${url}`);
        }
    });
}


for (let i = 0; i < all_canvas.length; i++) {
    let canvas = all_canvas[i];
    let seat_id = canvas.id;
    // console.log(seat_id);

    canvas.addEventListener("dblclick", function () {
        const g = document.getElementById(seat_id)
        console.log(seat_id)
        const qrBolock = g.parentElement.parentElement.parentElement
        qrBolock.remove();
    });


    // ORIGINAL: Using f2s.in URL shortener
    // let url = `https://f2s.in?id=${seat_id}`
    
    // TEMPORARY: Direct URL for testing (bypass f2s.in)
    let url = `https://calculatentrade.com/theatre/show-menu/${seat_id}`
    
    generateQRCode(`${seat_id}`, url)
}

function SmallQRCode() {
    let url = window.location.href;
    url = url.replace('new-seat-qr', 'seat-qr');

    window.open(url, '_self');
}

function LargeQRCode() {
    let url = window.location.href;
    url = url.replace('seat-qr', 'new-seat-qr');
    window.open(url, '_self');
}

