let messag = local_storage.getItem('message')
if (messag != null) {
    showToast('bg-danger', messag)
}

local_storage.clear()

let theatre_id = JSON.parse(document.getElementById('theatre-id').innerText)

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

let menu_data = {}
var commission = 0
var tax_type = "IGST"
async function loadMenu() {
    let menu_api_url = `/theatre/api/all-menu/${theatre_id}`;
    menu_data = await getRequest(menu_api_url);
    commission = menu_data.commission;
    tax_type = menu_data.tax_type;
    menu_data = menu_data.all_category;

    for (let i = 0; i < menu_data.length; i++) {
        let data = menu_data[i];

        if (i === 0) {
            showFoodItems(data, true);
        }
        else {
            showFoodItems(data, false);
        }
    }

}
// Update view cart position as per the category size
function updateCartPanelPosition() {
    const ul = document.getElementById('food-category-list');
    const cartPanel = document.querySelector('a.cart-panel');
    const blankDiv = document.querySelector('.blank-div');

    if (!ul || !cartPanel) return;

    const liCount = ul.querySelectorAll('li').length;

    cartPanel.classList.remove('PositionBottomless', 'PositionBottomMore');

    if (liCount <= 5) {
        cartPanel.classList.add('PositionBottomless');

    } else {
        cartPanel.classList.add('PositionBottomMore');
        blankDiv.classList.add('more-margin_bottom');
    }
}
// Call the function to update the cart panel position


// draggable cart-Panel
(function () {
    const cart = document.getElementById('cart-div');
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    cart.addEventListener('mousedown', function (e) {
        // Only drag when holding Shift key
        if (!e.shiftKey) return;

        isDragging = true;
        offsetX = e.clientX - cart.getBoundingClientRect().left;
        offsetY = e.clientY - cart.getBoundingClientRect().top;

        // prevent default click
        e.preventDefault();
        cart.style.position = 'fixed';
        cart.style.zIndex = 9999;
    });

    document.addEventListener('mousemove', function (e) {
        if (!isDragging) return;

        let x = e.clientX - offsetX;
        let y = e.clientY - offsetY;

        cart.style.left = `${x}px`;
        cart.style.top = `${y}px`;
        cart.style.right = 'auto';
        cart.style.bottom = 'auto';
    });

    document.addEventListener('mouseup', function () {
        isDragging = false;
    });
})();

// draggable cart-panel end

function showFoodItems(category_data, is_active) {
    // creating all food view
    let foodContent = document.getElementById('food-item-content');
    let div = document.createElement('div');
    div.setAttribute('id', `food-category-${category_data.id}`);
    if (is_active) {
        div.setAttribute('class', 'tab-pane fade show active')
    }
    else {
        div.setAttribute('class', 'tab-pane fade')
    }


    // /////////////////////////////////////////////////////////////////////////////////////
    // New code start for new food view
    let window_location = window.location.href;
    // if (window_location.includes('menu')) {
    let menu_footer = document.getElementById('food-category-list');
    let li = document.createElement('li');
    li.setAttribute('class', 'nav-item col-lg-2 col col-md-2 category-type-column');

    let col = document.createElement('a');

    col.setAttribute('href', `#food-category-${category_data.id}`);
    col.setAttribute('data-bs-toggle', "pill");

    if (window_location.includes('menu')) {

        col.setAttribute('class', 'col-lg-2 col col-md-2 category-type-column');
    }
    else {

        col.setAttribute('class', 'd-flex align-items-center text-start mx-3 ms-0 pb-3')
    }

    if (is_active == true) {
        col.classList.add('active');
        col.classList.add('show');
    }

    let html_data = '';
    let image_url = category_data.category_image

    if (window.location.href.includes('https')) {
        image_url = image_url.replace('http', 'https');
    }

    if (window_location.includes('menu')) {
        html_data = `<div class="category-card-link">
                <div class="category-type-card">
                    <div class="category-type-img-wrapper">
                        <img loading="lazy" src="${image_url}" alt="" class=" category-type-img">
                    </div>
                    <div class="category-type-name  text-white p-2">
                        <p class="mb-0">${category_data.name}</p>
                    </div>
                </div>
                </div>`
    }
    else {
        li.setAttribute('class', 'nav-item');
        html_data = `
        <div class="ps-3">
            <h6 class="mt-n1 mb-0">${category_data.name}</h6>
        </div>
        `;
    }

    col.innerHTML = html_data;
    li.appendChild(col);
    menu_footer.appendChild(li);
    updateCartPanelPosition();

    // }

    // New code ends here

    let new_div = document.createElement('div');
    new_div.setAttribute('class', 'row g-3 mb-3')

    let food_items = category_data.items
    for (let i = 0; i < food_items.length; i++) {
        let item_data = food_items[i];
        let food_card = document.createElement('div');
        food_card.setAttribute('class', 'col-lg-6 col-sm-6');
        food_card.setAttribute('id', `food-id-${item_data.item_id}`)

        let food_image_url = item_data.food_image
        if (window.location.href.includes('https')) {
            food_image_url = food_image_url.replace('http', 'https');
        }

        let food_card_html = `
                                            <div class="d-flex align-items-center menu-item my-food-card">
                                                <img loading="lazy" class="flex-shrink-0 img-fluid rounded menu-img"
                                                    src="${food_image_url}" alt="" style="width: 80px;">
                                                <div class="w-100 d-flex flex-column text-start ps-4">
                                                    <span class="item-pk" style="display: none;">${item_data.item_id}</span>
                                                    <span class="item-real-price d-none">${item_data.real_price}</span>
                                                    <h5 class="d-flex justify-content-start border-bottom pb-2">
                                                        <span class="${item_data.food_type}-icon item-type"></span><span
                                                            class="item-name">${item_data.name}</span>
                                                        <span class="text-primary float-end ms-auto d-flex">
                                                        ₹<span class="item-price d-none">
                                                                ${item_data.price}
                                                            </span>
                                                            <span class="item-price-new">
                                                                ${Math.round(item_data.price)}
                                                            </span>
                                                        </span>
                                                    </h5>
                                                    <small class="fst-italic item-description">
                                                        ${item_data.description}
                                                    </small>
                                                    <div class="row align-items-center justify-content-between mt-2">
                                                        <div class="col-lg-6 col-md-6 col-12 add-box">
                                                            <button class="add-to-cart btn btn-primary"
                                                                onclick="addToCart(this)">Add <i
                                                                    class="fas fa-cart-plus"></i></button>
                                                        </div>
                                                        <div class="row d-none remove-box">

                                                            <div class="col-lg-6 col-md-6 col-6">
                                                                <div class="quantity-controls" style="display: flex;">
                                                                    <button class="minus btn btn-primary"
                                                                        onclick="DecreseQuantity(this)">-</button>
                                                                    <span class="quantity">1</span>
                                                                    <button class="plus btn btn-primary"
                                                                        onclick="IncreseQuantity(this)">+</button>
                                                                </div>
                                                            </div>
                                                            <div
                                                                class="col-lg-6 col-md-6 col-6 text-md-end text-lg-end p-sm-0">
                                                                <button onclick="removeItem(this)"
                                                                    class="remove-from-cart btn text-primary text-capitalize p-sm-0"><i
                                                                        class="fas fa-trash me-2"></i>Remove
                                                                </button>
                                                            </div>
                                                        </div>
                                                    </div>

                                                </div>
                                            </div>
        `

        food_card.innerHTML = food_card_html;
        new_div.appendChild(food_card);
    }
    // add blank div in bottom
    food_card = document.createElement('div');
    food_card.setAttribute('class', 'blank-div');
    new_div.appendChild(food_card);

    div.appendChild(new_div);
    foodContent.appendChild(div);



    // scroll behaviour added by kanika -18 May-2024

    // Assign last-visible-item
    // let lastItem = new_div.lastElementChild.previousElementSibling; // skip blank-div
    // if (lastItem) {
    //     lastItem.classList.add('last-visible-item');
    // }

    // // Add scroll event listener once
    // if (!foodContent.hasScrollListener) {
    //     foodContent.hasScrollListener = true;

    //     foodContent.addEventListener('scroll', function () {
    //         let currentTabPane = document.querySelector('.tab-pane.active');
    //         let lastItem = currentTabPane?.querySelector('.last-visible-item');

    //         if (lastItem) {
    //             let rect = lastItem.getBoundingClientRect();
    //             let parentRect = foodContent.getBoundingClientRect();

    //             if (rect.top < parentRect.bottom && rect.bottom > parentRect.top) {
    //                 let currentActive = document.querySelector('.category-type-column a.active');
    //                 let nextCategoryTab = currentActive?.closest('li')?.nextElementSibling?.querySelector('a');

    //                 if (nextCategoryTab) {
    //                     let tab = new bootstrap.Tab(nextCategoryTab);
    //                     tab.show();
    //                 }
    //             }
    //         }
    //     });
    // }

    // end scroll behaviour added by kanika -18 May-2024






    //    scroll behaviour second code
    // // STEP 1: Assign last-visible-item to each category's last item (excluding blank div)
    // document.querySelectorAll('.tab-pane').forEach((pane) => {
    //     let items = pane.querySelectorAll('.col-lg-6'); // your actual item class
    //     if (items.length > 0) {
    //         let last = items[items.length - 1];
    //         last.classList.add('last-visible-item');
    //     }
    // });

    // // STEP 2: Add scroll handler once
    // if (!foodContent.hasScrollListener) {
    //     foodContent.hasScrollListener = true;

    //     let isSwitching = false;

    //     foodContent.addEventListener('scroll', function () {
    //         if (isSwitching) return; // prevent multiple tab changes

    //         let currentTabPane = document.querySelector('.tab-pane.active');
    //         let lastItem = currentTabPane?.querySelector('.last-visible-item');

    //         if (lastItem) {
    //             let rect = lastItem.getBoundingClientRect();
    //             let parentRect = foodContent.getBoundingClientRect();

    //             // Ensure the item is fully visible or nearing bottom
    //             if (rect.top < parentRect.bottom && rect.bottom > parentRect.top + 50) {
    //                 isSwitching = true;

    //                 let currentActive = document.querySelector('.category-type-column a.active');
    //                 let currentLi = currentActive.closest('li');
    //                 let nextLi = currentLi?.nextElementSibling;

    //                 if (nextLi) {
    //                     let nextTab = nextLi.querySelector('a');
    //                     if (nextTab) {
    //                         let bsTab = new bootstrap.Tab(nextTab);
    //                         bsTab.show();

    //                         // Wait a moment for transition before re-enabling scroll switch
    //                         setTimeout(() => {
    //                             isSwitching = false;
    //                         }, 300); // Adjust if needed
    //                     }
    //                 } else {
    //                     isSwitching = false;
    //                 }
    //             }
    //         }
    //     });
    // }
    // end

}

loadMenu()

