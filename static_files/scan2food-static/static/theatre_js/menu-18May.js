let messag = localStorage.getItem('message')
if (messag != null) {
    showToast('bg-danger', messag)
}

localStorage.clear()

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

    if (window_location.includes('menu')) {
        html_data = `<div class="category-card-link">
                <div class="category-type-card">
                    <div class="category-type-img-wrapper">
                        <img loading="lazy" src="${category_data.category_image}" alt="" class=" category-type-img">
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

        let food_card_html = `
                                            <div class="d-flex align-items-center menu-item my-food-card">
                                                <img loading="lazy" class="flex-shrink-0 img-fluid rounded menu-img"
                                                    src="${item_data.food_image}" alt="" style="width: 80px;">
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

    // new code added by kanika for on sctroll activate new category
// Identify the last item of this category
let lastItem = new_div.lastElementChild.previousElementSibling; // skip blank-div
if (lastItem) {
    lastItem.classList.add('last-visible-item');
}

// Add scroll event listener once
if (!foodContent.hasScrollListener) {
    foodContent.hasScrollListener = true;

    foodContent.addEventListener('scroll', function () {
        let lastItems = document.querySelectorAll('.last-visible-item');
        lastItems.forEach((item) => {
            let rect = item.getBoundingClientRect();
            let parentRect = foodContent.getBoundingClientRect();

            // Check if last item is near bottom of visible scroll area
            if (rect.top < parentRect.bottom && rect.bottom > parentRect.top) {
                let categoryId = item.closest('.tab-pane').id.replace('food-category-', '');

                let currentActive = document.querySelector('.category-type-column a.active');
                let nextCategoryTab = document.querySelector(`.category-type-column a[href="#food-category-${categoryId}"]`)?.closest('li')?.nextElementSibling?.querySelector('a');

                if (nextCategoryTab && currentActive !== nextCategoryTab) {
                    // Switch active tab
                    currentActive?.classList.remove('active', 'show');
                    nextCategoryTab.classList.add('active', 'show');

                    // Switch active content
                    let currentPane = document.querySelector(currentActive?.getAttribute('href'));
                    let nextPane = document.querySelector(nextCategoryTab.getAttribute('href'));
                    currentPane?.classList.remove('active', 'show');
                    nextPane?.classList.add('active', 'show');
                }
            }
        });
    });
}




    //end new code
}

loadMenu()

// {/* <div class="blank-div"
// "></div> */}