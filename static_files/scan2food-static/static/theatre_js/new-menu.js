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


document.addEventListener("DOMContentLoaded", function () {
    const categoryList = document.querySelectorAll('#food-category-list li');
    const cartPanel = document.querySelector('a.cart-panel');

    if (cartPanel) {
        if (categoryList.length > 5) {
            cartPanel.classList.add('PositionBottomMore');
            cartPanel.classList.remove('PositionBottomLess');
        } else {
            cartPanel.classList.add('PositionBottomLess');
            cartPanel.classList.remove('PositionBottomMore');
        }
    }
});


// Call the function to update the cart panel position

function showFoodItems(category_data, is_active) {

    // creating all food view
    let foodContent = document.getElementById('food-item-content');
    let div = document.createElement('div');
    div.setAttribute('id', `food-category-${category_data.id}`);
    div.setAttribute('class', 'food-category');


    // /////////////////////////////////////////////////////////////////////////////////////
    // New code start for new food view
    let window_location = window.location.href;
    // if (window_location.includes('menu')) {
    let menu_footer = document.getElementById('food-category-list');
    let li = document.createElement('li');
    li.setAttribute('class', 'nav-item col-lg-2 col col-md-2 category-type-column');

    let col = document.createElement('a');

    col.setAttribute('href', `#food-category-${category_data.id}`);

    if (window_location.includes('menu')) {

        col.setAttribute('class', 'col-lg-2 col col-md-2 category-type-column category-type-a-tag');
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
        col.setAttribute('data-bs-toggle', "pill");
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

    new_div_html = `
        <div class="col-lg-12 col-sm-12 text-start">
            <h4>
            ${category_data.name}
            </h4>
        </div>
    `
    new_div.innerHTML = new_div_html;

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
                                                            <span class="item-price-new d-none">
                                                                ${Math.round(item_data.price)}
                                                            </span>
                                                            <span class="item-price-new">
                                                                ${item_data.real_price}
                                                            </span>
                                                        </span>
                                                    </h5>
                                                    <small class="">It will take. .</small>
                                                    <small class="text-dark">${item_data.min_time} - ${item_data.max_time} minutes</small>
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
}

loadMenu()
// guru's code
// setTimeout(() => {

//     const container = document.getElementById('food-item-content');

//     // get the all sections
//     let sections = Array.from(container.querySelectorAll('.food-category'));

//     // Function to get offsetTop of each section
//     function getSectionOffsets() {
//         return sections.map(section => ({
//             element: section,
//             offsetTop: section.offsetTop
//         }));
//     }

//     // Store initial offsets
//     let offsets = getSectionOffsets();

//     // Recalculate offsets on resize (important if layout changes)
//     window.addEventListener('resize', () => {
//         offsets = getSectionOffsets();
//     });

//     window.addEventListener('scroll', () => {
//         const bottomY = window.scrollY + window.innerHeight - 300;

//         for (let i = 0; i < offsets.length; i++) {
//             const current = offsets[i];
//             const next = offsets[i + 1];

//             if (
//                 bottomY >= current.offsetTop &&
//                 (!next || bottomY < next.offsetTop)
//             ) {
//                 document.getElementsByClassName('category-type-a-tag active show')[0].classList.remove('active', 'show');
//                 document.getElementsByClassName('category-type-a-tag')[i].classList.add('active', 'show');


//                 // Optional: Add an active class to the current section
//                 sections.forEach(s => s.classList.remove('active'));
//                 current.element.classList.add('active');

//                 break;
//             }
//         }
//     });

// }, 2000);


// fixed code added by kanika

setTimeout(() => {
    const container = document.getElementById('food-item-content');
    const categoryLinks = document.querySelectorAll('.category-type-a-tag');
    const sections = Array.from(container.querySelectorAll('.food-category'));

    // Helper to get offsetTop of section relative to container
    function getOffsetTopRelativeToContainer(el, container) {
        let offsetTop = 0;
        while (el && el !== container) {
            offsetTop += el.offsetTop;
            el = el.offsetParent;
        }
        return offsetTop;
    }

    // Store all food-category section offsets
    function getSectionOffsets() {
        return sections.map(section => ({
            element: section,
            offsetTop: getOffsetTopRelativeToContainer(section, container)
        }));
    }

    let offsets = getSectionOffsets();

    window.addEventListener('resize', () => {
        offsets = getSectionOffsets();
    });

    // --- Scroll Lock ---
    let scrollLock = false;

    // --- Scroll Event (only works when scrollLock = false) ---
    // container.addEventListener('scroll', () => {
    //     if (scrollLock) return;

    //     const scrollTop = container.scrollTop;

    //     // Adjust based on how much margin you want above heading
    //     const threshold = scrollTop + 100;

    //     for (let i = 0; i < offsets.length; i++) {
    //         const current = offsets[i];
    //         const next = offsets[i + 1];

    //         if (
    //             threshold >= current.offsetTop &&
    //             (!next || threshold < next.offsetTop)
    //         ) {
    //             // Remove all active tags
    //             document.querySelectorAll('.category-type-a-tag.active').forEach(el => el.classList.remove('active'));
    //             categoryLinks[i].classList.add('active');

    //             // Remove all active sections
    //             sections.forEach(s => s.classList.remove('active'));
    //             current.element.classList.add('active');
    //             break;
    //         }
    //     }
    // });

    //     container.addEventListener('scroll', () => {
    //     if (scrollLock) return;

    //     const scrollTop = container.scrollTop;
    //     const containerHeight = container.clientHeight;
    //     const scrollHeight = container.scrollHeight;

    //     // Adjust based on how much margin you want above heading
    //     const threshold = scrollTop + 100;

    //     // Special case: If near the bottom, activate last category
    //     if (scrollTop + containerHeight >= scrollHeight - 10) {
    //         // Remove all active tags
    //         document.querySelectorAll('.category-type-a-tag.active').forEach(el => el.classList.remove('active'));
    //         categoryLinks[categoryLinks.length - 1].classList.add('active');

    //         // Remove all active sections
    //         sections.forEach(s => s.classList.remove('active'));
    //         sections[sections.length - 1].classList.add('active');

    //         return;
    //     }

    //     for (let i = 0; i < offsets.length; i++) {
    //         const current = offsets[i];
    //         const next = offsets[i + 1];

    //         if (
    //             threshold >= current.offsetTop &&
    //             (!next || threshold < next.offsetTop)
    //         ) {
    //             // Remove all active tags
    //             document.querySelectorAll('.category-type-a-tag.active').forEach(el => el.classList.remove('active'));
    //             categoryLinks[i].classList.add('active');

    //             // Remove all active sections
    //             sections.forEach(s => s.classList.remove('active'));
    //             current.element.classList.add('active');
    //             break;
    //         }
    //     }
    // });

    // --- Scroll Event (only works when scrollLock = false) ---
    container.addEventListener('scroll', () => {
        if (scrollLock) return;

        const scrollTop = container.scrollTop;
        const containerHeight = container.clientHeight;
        const scrollHeight = container.scrollHeight;

        // Adjust based on how much margin you want above heading
        const threshold = scrollTop + 100;

        // Special case: If near the bottom, activate last category
        if (scrollTop + containerHeight >= scrollHeight - 10) {
            document.querySelectorAll('.category-type-a-tag.active').forEach(el => el.classList.remove('active'));
            categoryLinks[categoryLinks.length - 1].classList.add('active');

            sections.forEach(s => s.classList.remove('active'));
            sections[sections.length - 1].classList.add('active');

            return;
        }

        for (let i = 0; i < offsets.length; i++) {
            const current = offsets[i];
            const next = offsets[i + 1];

            if (
                threshold >= current.offsetTop &&
                (!next || threshold < next.offsetTop)
            ) {
                document.querySelectorAll('.category-type-a-tag.active').forEach(el => el.classList.remove('active'));
                categoryLinks[i].classList.add('active');

                sections.forEach(s => s.classList.remove('active'));
                current.element.classList.add('active');
                break;
            }
        }
    });

    // --- Click Event ---
    categoryLinks.forEach((link, index) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Lock scroll updates
            scrollLock = true;

            // Remove all active states and set clicked active
            document.querySelectorAll('.category-type-a-tag.active').forEach(el => el.classList.remove('active'));
            link.classList.add('active');

            sections.forEach(s => s.classList.remove('active'));
            sections[index].classList.add('active');

            // Scroll to the food category (with offset)
            const targetScrollTop = getOffsetTopRelativeToContainer(sections[index], container) - 20;

            container.scrollTo({
                top: targetScrollTop < 0 ? 0 : targetScrollTop,
                behavior: 'smooth'
            });

            // After scrolling completes, release scrollLock so manual scroll updates active class again
            setTimeout(() => {
                scrollLock = false;
            }, 600);

            // Also, listen for manual scrolls to release lock immediately
            const onManualScroll = () => {
                scrollLock = false;
                container.removeEventListener('scroll', onManualScroll);
            };
            container.addEventListener('scroll', onManualScroll);
        });
    });


    // --- Click Event ---
    categoryLinks.forEach((link, index) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Lock scroll updates
            scrollLock = true;

            // Remove all active states
            document.querySelectorAll('.category-type-a-tag.active').forEach(el => el.classList.remove('active'));
            link.classList.add('active');

            sections.forEach(s => s.classList.remove('active'));
            sections[index].classList.add('active');

            // Scroll to the food category (with offset)
            const targetScrollTop = getOffsetTopRelativeToContainer(sections[index], container) - 20;

            container.scrollTo({
                top: targetScrollTop < 0 ? 0 : targetScrollTop,
                behavior: 'smooth'
            });

            // Release lock after scrolling completes (approx 500ms)
            setTimeout(() => {
                scrollLock = false;
            }, 600);
        });
    });
}, 2000);










