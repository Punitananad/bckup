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

async function updateRefundQueryStatus(refundQueryId) {
    const btn = document.getElementById(`btn-${refundQueryId}`);

    if (btn.classList.contains('btn-success')) {
        showToast('bg-danger', 'Refund Query is already resolved');
        return;
    }
    const url = `/theatre/api/update-refund-query-status/${refundQueryId}`;
    const data = await getRequest(url);
    if (data.status == 'success') {
        showToast('bg-success', data.message);
        btn.setAttribute('class', 'btn btn-sm btn-success');
        btn.innerText = 'Resolved';
    }
    else {
        showToast('bg-danger', data.message);
        btn.setAttribute('class', 'btn btn-sm btn-success');
        btn.innerText = 'Resolved';
    }
}
