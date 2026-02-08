// get all orders

var all_order_data = {};

function saveOrderData(order_data) {
    const theatre_id = order_data.theatre_id;
    if (!all_order_data[`theatre-id-${theatre_id}`]) {
        all_order_data[`theatre-id-${theatre_id}`] = {
            theatre_id: theatre_id,
            theatre_name: order_data.theatre_name,
            orders: [],
            last_order_time: order_data.payment_time,
        };
    }

    const orders = all_order_data[`theatre-id-${theatre_id}`].orders;

    // find the index of existing order
    const existingIndex = orders.findIndex(o => o.order_id === order_data.order_id);

    if (existingIndex !== -1) {
        // replace existing order
        orders[existingIndex] = order_data;
    } else {
        // push new order
        orders.push(order_data);
    }



    const sorted_data = orders.sort((a, b) => b.payment_time - a.payment_time)

    const unseen_orders = sorted_data.filter(o => o.is_shown === false).length;

    const total_orders = sorted_data.length;

    all_order_data[`theatre-id-${theatre_id}`].orders = sorted_data;
    order_data.unseen_orders = unseen_orders;
    order_data.total_orders = total_orders;

    const task = { 'task': 'add-order', 'order_data': order_data };
    postMessage(task)

}

function removeOrderData(order_id, theatre_id) {
    const theatre_key = `theatre-id-${theatre_id}`;
    if (Object.keys(all_order_data).includes(theatre_key)) {
        // filter out the order with the given order_id;
        const orders = all_order_data[theatre_key].orders;
        const new_orders = orders.filter(order => order.order_id !== order_id);

        const sorted_data = new_orders.sort((a, b) => b.payment_time - a.payment_time);

        all_order_data[theatre_key].orders = sorted_data;

        const order_count = sorted_data.length;

        let last_order_time

        if (order_count === 0) {
            // remove the theatre
            delete all_order_data[theatre_key]
            last_order_time = 0;
        }
        else {
            last_order_time = sorted_data[0].payment_time
        }
        const task = { task: 'update-deleted-order', order_count: order_count, last_order_time: last_order_time, theatre_id: theatre_id };
        postMessage(task);
    }


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

async function getAllOrders() {
    const url = `/theatre/api/live-orders`
    const allRunningOrders = await getRequest(url);

    for (const order in allRunningOrders) {
        const order_data = allRunningOrders[order];
        saveOrderData(order_data);
    }

}


function updateSeenOrder(order_id, theatre_id) {
    const theatre_key = `theatre-id-${theatre_id}`;
    if (Object.keys(all_order_data).includes(theatre_key)) {
        let orders = all_order_data[theatre_key].orders;
        let new_orders = []
        const order_count = orders.length;

        let seen_orders = 0
        for (let i = 0; i < orders.length; i++) {
            const element = orders[i];

            new_orders.push(element);
            if (element.id == order_id) {
                element.view_status = true;
            }

            if (element.view_status == false) {
                seen_orders += 1;
            }
        };

        const sorted_data = new_orders.sort((a, b) => b.payment_time - a.payment_time);

        all_order_data[theatre_key].orders = sorted_data;

        const task = { task: 'update-deleted-order', order_count: order_count, theatre_id: theatre_id, seen_orders: seen_orders };
        postMessage(task);
    }
}


self.onmessage = async (e) => {
    const data = e.data;
    const task = data.task;

    if (task === 'get-all-orders') {
        await getAllOrders();
    }

    else if (task === 'get-all-orders-of-theatre') {
        const theatre_id = data.theatre_id;
        const task = { 'task': 'theatre-orders', 'order_data': all_order_data[`theatre-id-${theatre_id}`] };
        postMessage(task);
    }


    else if (task === 'get-all-orders-data') {
        const task = { 'task': 'all-orders-data', 'order_data': all_order_data };
        postMessage(task);
    }

    else if (task === 'add-new-order') {
        const order_data = data.order_data
        saveOrderData(order_data);
    }

    else if (task === 'delete-order') {
        const theatre_id = data.theatre_id;
        const order_id = data.order_id;
        removeOrderData(order_id, theatre_id);
    }

    else if (task === 'order-seen') {
        const theatre_id = data.theatre_id;
        const order_id = data.order_id;
        updateSeenOrder(order_id, theatre_id);
    }
}