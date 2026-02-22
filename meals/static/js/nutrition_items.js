document.addEventListener('DOMContentLoaded', function () {
    const foodItems = []; // Array to store selected items

    // DOM Elements
    const addBtn = document.getElementById('add_food_btn');
    const itemsTableBody = document.querySelector('#food_items_table tbody');
    const itemsJsonInput = document.getElementById('id_items_json');

    // Totals Display
    const totalCarbsSpan = document.getElementById('total_carbs');
    const totalProteinSpan = document.getElementById('total_protein');
    const totalFatsSpan = document.getElementById('total_fats');

    // Inputs
    const foodIdInput = document.getElementById('id_food_item');
    const qtyInput = document.getElementById('id_quantity_g');

    // External Elements (from food_search.js)
    const clearBtn = document.getElementById('clear_food_selection');
    const selectedDisplay = document.getElementById('selected_food_display');
    const searchInput = document.getElementById('food_search_input');

    // Add Food Handler
    if (addBtn) {
        addBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const foodId = foodIdInput.value;
            const qty = parseFloat(qtyInput.value);

            if (!foodId) {
                alert("Please select a food item first.");
                return;
            }
            if (!qty || qty <= 0) {
                alert("Please enter a valid quantity.");
                return;
            }

            // Retrieve food data from hidden input dataset (populated by food_search.js)
            let foodData = null;
            try {
                if (foodIdInput.dataset.currentFood) {
                    foodData = JSON.parse(foodIdInput.dataset.currentFood);
                }
            } catch (err) {
                console.error("Error parsing food data", err);
            }

            if (!foodData) {
                alert("Error retrieving food details. Please search again.");
                return;
            }

            // Calculate Item Macros
            const ratio = qty / 100.0;
            const itemCarbs = (foodData.carbs * ratio).toFixed(1);
            const itemProtein = (foodData.protein * ratio).toFixed(1);
            const itemFats = (foodData.fats * ratio).toFixed(1);

            // Add to array
            const newItem = {
                id: foodData.id,
                name: foodData.name,
                qty: qty,
                carbs: parseFloat(itemCarbs),
                protein: parseFloat(itemProtein),
                fats: parseFloat(itemFats)
            };

            foodItems.push(newItem);

            // Render and Update
            renderTable();
            resetInputs();
        });
    }

    function renderTable() {
        itemsTableBody.innerHTML = '';

        let tCarbs = 0, tProtein = 0, tFats = 0;

        foodItems.forEach((item, index) => {
            tCarbs += item.carbs;
            tProtein += item.protein;
            tFats += item.fats;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.qty}g</td>
                <td>${item.carbs}g</td>
                <td>${item.protein}g</td>
                <td>${item.fats}g</td>
                <td>
                    <button type="button" class="btn link small remove-item" data-index="${index}" style="color:red;">Remove</button>
                </td>
            `;
            itemsTableBody.appendChild(row);
        });

        // Update Totals Display
        totalCarbsSpan.textContent = tCarbs.toFixed(1);
        totalProteinSpan.textContent = tProtein.toFixed(1);
        totalFatsSpan.textContent = tFats.toFixed(1);

        // Update Hidden Input
        itemsJsonInput.value = JSON.stringify(foodItems);

        // Bind Remove Buttons
        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', function () {
                const idx = parseInt(this.dataset.index);
                foodItems.splice(idx, 1);
                renderTable();
            });
        });
    }

    function resetInputs() {
        // Clear inputs using the Clear button logic from food_search.js if possible, 
        // or manually reset to avoid conflict.

        // Reset Logic:
        foodIdInput.value = '';
        delete foodIdInput.dataset.currentFood;
        qtyInput.value = '';

        // Hide Display UI (manual emulation of clear_food_selection click behavior without keeping event listeners messy)
        selectedDisplay.style.display = 'none';
        clearBtn.style.display = 'none';
        searchInput.style.display = 'block';
        searchInput.value = '';

        // Reset required attr if manually set?
        // Rely on toggleManualInputs from existing code if it exists.
    }
});
