// CODE FOR DATE RANGE FILTER

$(document).ready(function () {
    $('#daterange').daterangepicker({
        locale: {
            format: 'DD/MMM/YYYY'
        },
        startDate: new Date(moment()), // Set start date to today
        endDate: new Date(moment().add(1, 'days')),   // Set end date to today
        showDropdowns: true,
        opens: 'right',
        ranges: {
            'Today': [moment(), moment().add(1, 'days')],
            'Yesterday': [moment().subtract(1, 'days'), moment()],
            'Last 7 Days': [moment().subtract(6, 'days'), moment().add(1, 'days')],
            'Last 30 Days': [moment().subtract(29, 'days'), moment().add(1, 'days')],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().startOf('month')]
        }
    });
});


const perms = new URLSearchParams(window.location.search)

var all_parimeters = {}

for (const [key, value] of perms.entries()) {
    all_parimeters[key] = value;
}


let daterange = all_parimeters.daterange

if (daterange === undefined) {
    daterange = "";
}

let orderStatus = all_parimeters['order-status']
if (orderStatus === undefined) {
    orderStatus = "Success";
}

const selectedTheatre = document.getElementById('selected-theatre-id').value;

let page = all_parimeters['page']
if (page === undefined) {
    page = 0;
}


function showOrders(order_list) {
    const tbody = document.getElementById('all-orders-tbody');
    tbody.innerHTML = ""
    for (let i = 0; i < order_list.length; i++) {
        const order_data = order_list[i];
        const tr = document.createElement('tr');

        var payment_status = {}
        if (order_data.payment_status == 'Success') {
            payment_status['class'] = 'badge bg-success'
            payment_status['status'] = 'Success'
        }
        else {
            payment_status['class'] = 'badge bg-danger'
            payment_status['status'] = order_data.payment_status
        }

        var view_status = {}
        if (order_data.view_status) {
            view_status.class = 'badge bg-success'
            view_status.status = 'Seen'
        }
        else {
            view_status.class = 'badge bg-danger'
            view_status.status = 'Not Seen !'
        }

        tr_html = `
            <th>
                ${order_data.seat}
            </th>
            <td>
                ${order_data.payment_time.replace("|", " , ")}
            </td>
            <td class="text-center">
                ₹ ${order_data.order_amount}
            </td>
            <td class="text-center">
                ${order_data.quantity}
            </td>
            <td>
                ${order_data.taken_by}
            </td>
            <td>
                ${order_data.deliverd_by}
            </td>
            <td>
                <span class="${payment_status.class}">
                    ${payment_status.status}
                </span>
            </td>
            <td>
                <a class="me-3" href="/theatre/order-profile/${order_data.id}">
                    <i class="fas fa-eye text-primary"></i>
                </a>
            </td>
        `
        tr.innerHTML = tr_html;
        tbody.appendChild(tr);
    }
}


const worker = new Worker('/static/theatre_js/all-orders/worker.js');

function downloadReport() {
    task = { task_name: 'get-order-data' }
    worker.postMessage(task);
}

function getAllOrders(daterange, orderStatus, selectedTheatre, page) {
    const task = { task_name: 'get-all-orders', daterange: daterange, order_status: orderStatus, selected_theatre: selectedTheatre, page: page }
    worker.postMessage(task)
}

getAllOrders(daterange, orderStatus, selectedTheatre, page);

// It will show the card data...
function showCardData(theatre_amount, total_amount, net_profit, order_count) {
    document.getElementById('theatre_amount').innerText = theatre_amount;
    document.getElementById('order_count').innerText = order_count;
}


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



worker.onmessage = (e) => {
    const task_detail = e.data;
    const task_name = task_detail.task_name;

    if (task_name === 'update-card') {
        const theatre_amount = task_detail.theatre_amount;
        const total_amount = task_detail.total_amount;
        const net_profit = task_detail.net_profit;
        const order_count = task_detail.order_count;
        showCardData(theatre_amount, total_amount, net_profit, order_count)
        const downloadButton = document.getElementById('download-report')
        downloadButton.classList.remove('d-none');
    }

    else if (task_name === 'show-orders') {
        const orders = task_detail.orders;
        showOrders(orders);
        updatePaginationUI(task_detail.current_page, task_detail.total_pages);
    }

    else if (task_name === 'generate-excel') {
        const daterange = document.getElementById('daterange').value;
        const excel_data = task_detail.data;
        // convert the data into excel data.
        const ws = XLSX.utils.aoa_to_sheet(excel_data); // Convert array to worksheet
        const wb = XLSX.utils.book_new();         // Create a new workbook
        XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
        XLSX.writeFile(wb, `report${daterange}.xlsx`);
    }
}

function updatePaginationUI(currentPage, totalPages) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = '';

    for (let i = 0; i < totalPages; i++) {
        const btn = document.createElement('button');
        btn.innerText = i + 1;

        // Highlight current page based on URL or click
        if (i === parseInt(currentPage)) {
            btn.classList.add('btn', 'btn-sm', 'btn-primary', 'm-2');
        } else {
            btn.classList.add('btn', 'btn-sm', 'btn-secondary', 'm-2');
        }

        btn.addEventListener('click', () => {
            page = i;
            history.replaceState(null, null, updateURLParam("page", i));
            worker.postMessage({ task_name: 'paginate', page: i });
        });

        paginationContainer.appendChild(btn);
    }
}



function updateURLParam(key, value) {
    const url = new URL(window.location);
    url.searchParams.set(key, value);
    return url.toString();
}


setTimeout(() => {
    if (daterange !== "") {
        document.getElementById('daterange').value = daterange;
    }
    document.getElementById('order-status').value = orderStatus;

}, 200);
