// function on add to cart button
function addToCart(btn) {
    // adding the active class to complet card
    btn.parentElement.parentElement.parentElement.parentElement.classList.add('active')
    // getting the card so we can get the item details
    let card = btn.parentElement.parentElement.parentElement.parentElement
    // fetching the details from card

    let table_name = document.getElementById('menuePopUpLabel').innerText;

    let item_name = card.getElementsByClassName('item-name')[0].innerText;
    let item_type = card.getElementsByClassName('item-type')[0].classList.value
    item_type = item_type.replaceAll('-icon item-type', '');
    let item_price = JSON.parse(card.getElementsByClassName('item-price')[0].innerText);
    let item_description = card.getElementsByClassName('item-description')[0].innerText;
    let item_real_price = card.getElementsByClassName('item-real-price')[0].innerText

    // getting the food item id
    let pk = card.getElementsByClassName('item-pk')[0].innerText;
    // creating data to save in local storage

    let append_data = {}
    append_data['item_type'] = item_type
    append_data['name'] = item_name;
    append_data['item_price'] = item_price;
    append_data['item_real_price'] = item_real_price
    append_data['item_description'] = item_description;
    append_data.quantity = 1;
    // make add box d-none
    card.getElementsByClassName('add-box')[0].classList.add('d-none')
    // remove remove box d-none
    card.getElementsByClassName('remove-box')[0].classList.remove('d-none')
    // set Quantity 1
    card.getElementsByClassName('quantity')[0].innerText = 1

    // getting the data from local storage
    let table_cart_data = local_storage.getItem(table_name)

    // making the data readbale
    table_cart_data = JSON.parse(table_cart_data)

    // updating the data
    table_cart_data[pk] = append_data
    json_data = JSON.stringify(table_cart_data)

    // saving new data to local storage
    local_storage.setItem(table_name, json_data)
    // updating the cart lenght

    UpdateCart(table_name)

}


// decrese the quantity in cart
function IncreseQuantity(btn) {
    let table_name = document.getElementById('menuePopUpLabel').innerText;

    // getting the parentDiv
    let parentDiv = btn.parentElement.parentElement.parentElement.parentElement.parentElement;

    // getting the pk
    let pk = parentDiv.getElementsByClassName('item-pk')[0].innerText;

    // making ui and better experience
    let big_box = btn.parentElement;
    let quantity_box = big_box.getElementsByClassName('quantity')[0]
    let quantity = Number(quantity_box.innerText);

    // increse the quantity
    quantity += 1;
    quantity_box.innerText = quantity;

    // get data from local storage
    let table_cart_data = local_storage.getItem(table_name);

    // convert local data into dictionary
    table_cart_data = JSON.parse(table_cart_data);

    // update the data
    table_cart_data[pk].quantity = quantity;

    // again making data as for saving purpose
    table_cart_data = JSON.stringify(table_cart_data)

    // save cart data in local storage
    local_storage.setItem(table_name, table_cart_data)

    // updating the cart lenght
    UpdateCart(table_name)

}

function DecreseQuantity(btn) {
    let table_name = document.getElementById('menuePopUpLabel').innerText;

    let parentDiv = btn.parentElement.parentElement.parentElement.parentElement.parentElement;

    // getting the pk
    let pk = parentDiv.getElementsByClassName('item-pk')[0].innerText;

    // making ui and better experience
    let big_box = btn.parentElement;
    let quantity_box = big_box.getElementsByClassName('quantity')[0]
    let quantity = Number(quantity_box.innerText);

    // increse the quantity
    quantity -= 1;
    if (quantity >= 1) {
        quantity_box.innerText = quantity;

        // get data from local storage
        let table_cart_data = local_storage.getItem(table_name);

        // convert local data into dictionary
        table_cart_data = JSON.parse(table_cart_data);

        // update the data
        table_cart_data[pk].quantity = quantity;

        // again making data as for saving purpose
        table_cart_data = JSON.stringify(table_cart_data)

        // save cart data in local storage
        local_storage.setItem(table_name, cart_data)
    }

    else {
        parentDiv.getElementsByClassName('remove-from-cart')[0].click()
    }

    // updating the cart lenght
    UpdateCart(table_name)

}

function removeItem(btn) {
    let table_name = document.getElementById('menuePopUpLabel').innerText;

    let parentDiv = btn.parentElement.parentElement.parentElement.parentElement.parentElement;

    // remove active class
    parentDiv.classList.remove('active');

    // getting the pk
    let pk = parentDiv.getElementsByClassName('item-pk')[0].innerText;

    // get cart_data from local storage
    let table_cart_data = local_storage.getItem(table_name);

    // convert from json to dictionary
    table_cart_data = JSON.parse(table_cart_data);

    // updateing the data for saving
    delete table_cart_data[pk];

    // save in cart data
    table_cart_data = JSON.stringify(table_cart_data)
    local_storage.setItem(table_name, table_cart_data)

    // remove remove-box d-none
    parentDiv.getElementsByClassName('remove-box')[0].classList.add('d-none');

    // adding d-none to add-box
    parentDiv.getElementsByClassName('add-box')[0].classList.remove('d-none');

    // updating the cart lenght
    UpdateCart(table_name)
}

function UpdateCart(table_name) {

    // getting the data of this table
    let table_cart_data = local_storage.getItem(table_name);
    table_cart_data = JSON.parse(table_cart_data);
    let cart_length = Object.keys(table_cart_data).length;

    if (cart_length == 0) {
        document.getElementById('cart-div').setAttribute('disabled', '');
        if (window.location.href.includes('menu')) {
            document.getElementById('cart-div').setAttribute('style', 'display: none;');
        }
    }
    else {
        document.getElementById('cart-div').removeAttribute('disabled');
        if (window.location.href.includes('menu')) {
            document.getElementById('cart-div').setAttribute('style', 'display: block');
        }
    }
    document.getElementById('cart-length').innerText = cart_length;
    
    // Check if getCartAmount exists (from cart.js), otherwise skip
    if (typeof getCartAmount === 'function') {
        getCartAmount(table_cart_data);
    } else {
        console.warn('getCartAmount function not found - cart.js may not be loaded yet');
    }
}



// load existing cart
function loadExistingCart(table_name) {

    let myFoodCards = document.getElementsByClassName('my-food-card');

    let table_cart_data = local_storage.getItem(table_name);
    table_cart_data = JSON.parse(table_cart_data);


    for (let i = 0; i < myFoodCards.length; i++) {
        let foodCard = myFoodCards[i];
        let status;
        if (foodCard.classList.contains('active')) {
            status = true
            let removeItemButton = foodCard.getElementsByClassName('remove-from-cart')[0]
            let parentDiv = removeItemButton.parentElement.parentElement.parentElement.parentElement.parentElement;

            // remove remove-box d-none
            parentDiv.getElementsByClassName('remove-box')[0].classList.add('d-none');

            // adding d-none to add-box
            parentDiv.getElementsByClassName('add-box')[0].classList.remove('d-none');

        }
        else {
            status = false
        }

        if (status === true) {
            foodCard.classList.remove('active');
        }

    }

    for (let i in table_cart_data) {
        // tet the table id
        let tab_id = `food-id-${i}`
        // get the card
        let card = document.getElementById(tab_id);
        // make the item
        let active_tab = card.getElementsByClassName('menu-item')[0];
        // make the item highlight
        active_tab.classList.add('active');
        // make add box d-none
        card.getElementsByClassName('add-box')[0].classList.add('d-none');
        // remove remove box d-none
        card.getElementsByClassName('remove-box')[0].classList.remove('d-none');
        // set Quantity 1
        card.getElementsByClassName('quantity')[0].innerText = table_cart_data[i]['quantity'];
    }

    let cart_length = Object.keys(table_cart_data).length;
    document.getElementById('cart-length').innerText = cart_length;

    if (cart_length === 0) {
        document.getElementById('cart-div').setAttribute('disabled', '');
    }

}
