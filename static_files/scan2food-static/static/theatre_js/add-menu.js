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

var selected_food_id = "";

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
            console.error('Error:', error);
            throw new Error('Failed to fetch data');
        });
}

const add_url = document.getElementById('item-form').action

var all_images = [];

function OpenAddItem(id) {
    document.getElementById('id_catogary').value = id;
    document.getElementById('id_name').value = "";
    document.getElementById('id_food_image').value = '';
    document.getElementById('id_price').value = "";
    document.getElementById('id_description').value = "";
    document.getElementById('id_priority_number').value = "";

    document.getElementById('item-form').action = add_url;

}

function EditItem(id, button, food_id) {
    document.getElementById('item-form').action = `${add_url}/${food_id}`
    document.getElementById('id_catogary').value = id;
    div = button.parentElement.parentElement.parentElement;
    food_type = div.getElementsByClassName('food-type')[0].classList.value;
    food_name = div.getElementsByClassName('food-name')[0].innerText;
    made_by = div.getElementsByClassName('made-by')[0].innerText;
    food_price = div.getElementsByClassName('food-price')[0].innerText;
    min_time = JSON.parse(div.getElementsByClassName('min-time')[0].innerText);
    max_time = JSON.parse(div.getElementsByClassName('max-time')[0].innerText);
    food_description = div.getElementsByClassName('food-description')[0].innerText;
    priority_number = div.getElementsByClassName('priority-number')[0].innerText

    food_type = food_type.replaceAll('-icon food-type', '')

    document.getElementById('id_food_type').value = food_type;
    document.getElementById('id_name').value = food_name;
    document.getElementById('id_made_by').value = made_by;
    document.getElementById('id_price').value = food_price;
    document.getElementById('id_min_time').value = min_time;
    document.getElementById('id_max_time').value = max_time;
    document.getElementById('id_description').value = food_description;
    document.getElementById('id_priority_number').value = priority_number;

    document.getElementById('sell-for-mrp').setAttribute('item-id', food_id);

}

function DeleteItem(id) {
    document.getElementById('deleted-item-id').value = id;
    $("#deleteItem").modal('show');
}

function deleteCategory(id) {
    document.getElementById('delete-category-form').action = `/theatre/delete-food-category/${id}`
    $("#deleteCategory").modal("show");
}

async function openImagePopUp(img, id, food_name) {
    // get all images from api
    if (all_images.length == 0) {
        // get all images
        let url = `/theatre/api/get-all-images`

        // galery div
        let modal = document.getElementById('imageModal');
        let galery = modal.getElementsByClassName('modal-body')[0];
        let div = document.createElement('div');
        div.setAttribute('class', 'row');

        let images = await getRequest(url);
        all_images = images['images'];

        for (let i = 0; i < all_images.length; i++) {
            let img_src = all_images[i];
            div.innerHTML += `<div class="col-3">
            <img loading="lazy" src="${img_src}" class="img-thumbnail" alt="image" onclick="UploadImage(this)">
            </div>
            `
            galery.appendChild(div);
        }

    }
    selected_food_id = id;

    document.getElementById('imageModalLabel').innerText = `Select Image from galery for ${food_name}`;
    // show pupup
    $('#imageModal').modal('show');
}

async function UploadImage(img) {
    food_id = selected_food_id
    old_food_image = document.getElementById(`food-id-${food_id}`)
    // hit upload image api
    let url = `/theatre/api/upload-food-image`
    let upload_data = {
        'food_id': food_id,
        'image_url': img.src
    }
    
    data = await PostRequest(url, upload_data);

    if (data['message'] == 'Image Uploaded') {
        // update image
        old_food_image.src = img.src;
    }
    else {
        alert(data['message']);
    }

    $('#imageModal').modal('hide');
}

function countMadeBy() {
    let all_made_by = document.getElementsByClassName('made-by');
    for (let i = 0; i < all_made_by.length; i++) {

        let num = 0;

        switch (all_made_by[i].innerText) {

            case 'packaged':
                num = document.getElementById('packaged-count').innerText
                num = parseInt(num) + 1;
                document.getElementById('packaged-count').innerText = num;
                break;

            case 'in-house':
                num = document.getElementById('in-house-count').innerText
                num = parseInt(num) + 1;
                document.getElementById('in-house-count').innerText = num;
                break;

            case 'third-party':
                num = document.getElementById('third-party-count').innerText
                num = parseInt(num) + 1;
                document.getElementById('third-party-count').innerText = num;
                break;
        }

        // show the count value in all items
        document.getElementById('total-count').innerText = all_made_by.length;

    }
}

function openDeactivatePopUp(button) {
    // show the poupup
    const count_value = button.getElementsByClassName('count-value')[0].innerText;
    document.getElementById('total-items').innerText = count_value;
    const headingLabel = document.getElementById('DeactivateCategoryLabel');
    let category_name = button.innerText;
    category_list = category_name.split(" ");
    category_list.pop();

    category_name = String(category_list.join(" "));


    headingLabel.innerText = `${category_name}`;
    showItems()
    const parentDiv = button.parentElement
    const buttons = parentDiv.getElementsByClassName('btn')
    for (let i = 0; i < buttons.length; i++) {
        if (buttons[i] == button) {
            buttons[i].setAttribute('class', 'btn btn-success ms-2');
        }
        else {
            buttons[i].setAttribute('class', 'btn btn-primary ms-2');
        }
    }
}

function showItems() {
    let category_name = document.getElementById('DeactivateCategoryLabel').innerText;
    // hide all the items with class item-ids
    const all_items = document.getElementsByClassName('item-ids');
    category_name = category_name.replaceAll(' ', '-').toLowerCase();

    let show_value = 0;
    for (let i = 0; i < all_items.length; i++) {
        const item = all_items[i];
        const made_by = item.getElementsByClassName('made-by')[0].innerText;
        if (category_name == 'all') {
            item.classList.remove('d-none');
            show_value += 1;
        }
        else if (made_by !== category_name) {
            item.classList.add('d-none');
        }

        else {
            show_value += 1;
            item.classList.remove('d-none');
        }
    }
    document.getElementById('item-count').innerText = show_value;
}

async function updateBulkStatus(button) {
    // get the status
    var status = ""
    if (button.innerText == 'Deactivate Items') {
        status = 'deactivate'
    }
    else {
        status = 'activate'
    }
    // get the made by
    const made_by = document.getElementById('DeactivateCategoryLabel').innerText.replaceAll(' ', '-').toLowerCase();
    const url = `/theatre/api/update-bulk-status?made_by=${made_by}&status=${status}`;
    const data = await getRequest(url);
    
    alert(data['message']);
    window.location.reload();
    

}

countMadeBy()

function showActionPopup() {
    // get the active button
    const totalCount = document.getElementById('total-count');
    parentElement = totalCount.parentElement.parentElement;
    const all_buttons = parentElement.getElementsByClassName('btn');
    for (let i = 0; i < all_buttons.length; i++) {
        if (all_buttons[i].classList.contains('btn-success')) {
            all_buttons[i].click();
            break;
        }
        else {
            continue;
        }
    }
    $("#DeactivateCategory").modal('show')
}

const all_is = document.getElementsByClassName('item-ids');
document.getElementById('item-count').innerText = all_is.length;