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

async function updateRefundQuery() {
    const url = '/theatre/api/refund-query-count?user=admin';
    
    const count_data = await getRequest(url);
    const query_a_tag = document.getElementById('refund-queries');
    
    if (count_data.count != 0) {
        query_a_tag.innerHTML = `Refund Queries <span class="badge bg-danger">${count_data.count}</span>`;
    }
}

window.onload = updateRefundQuery();
