let user_type_select = document.getElementById('id_user_type');

function createTypeSelect() {
    const groups = {'Customer Associate': 'Customer Associate', 'manager': 'Manager'}

    for (let i in groups) {
        let option = document.createElement('option');
        option.value = i;
        option.innerText = groups[i];
        user_type_select.appendChild(option);
    }
}

createTypeSelect()