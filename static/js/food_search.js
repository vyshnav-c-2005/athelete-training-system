document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('food_search_input');
    const resultsDiv = document.getElementById('food_search_results');
    const hiddenInput = document.getElementById('id_food_item');
    const selectedDisplay = document.getElementById('selected_food_display');
    const clearBtn = document.getElementById('clear_food_selection');

    let debounceTimer;

    // Search input handler
    function performSearch(query) {
        fetch(`/meals/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(err => console.error('Error fetching foods:', err));
    }

    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.trim();
        clearTimeout(debounceTimer);

        // Removed length check to allow 1-char search
        debounceTimer = setTimeout(() => {
            performSearch(query);
        }, 300);
    });

    // Show common foods on focus if empty
    searchInput.addEventListener('focus', function () {
        if (!searchInput.value.trim()) {
            performSearch('');
        }
    });

    // Display search results
    function displayResults(foods) {
        resultsDiv.innerHTML = '';
        if (foods.length === 0) {
            const noRes = document.createElement('div');
            noRes.className = 'search-result-item no-result';
            noRes.textContent = 'No matching foods found.';
            resultsDiv.appendChild(noRes);
            resultsDiv.style.display = 'block';
            return;
        }

        foods.forEach(food => {
            const div = document.createElement('div');
            div.className = 'search-result-item';
            div.textContent = `${food.name} (C:${food.carbs} P:${food.protein} F:${food.fats})`;
            div.dataset.id = food.id;
            div.dataset.json = JSON.stringify(food);

            div.addEventListener('click', function () {
                selectFood(food);
            });

            resultsDiv.appendChild(div);
        });
        resultsDiv.style.display = 'block';
    }

    // Handle food selection
    function selectFood(food) {
        // Update hidden input
        hiddenInput.value = food.id;

        // Update display
        searchInput.value = ''; // Clear search
        resultsDiv.style.display = 'none'; // Hide results

        selectedDisplay.innerHTML = `
            <strong>Selected:</strong> ${food.name} 
            <span class="macro-badge">C: ${food.carbs}g</span>
            <span class="macro-badge">P: ${food.protein}g</span>
            <span class="macro-badge">F: ${food.fats}g</span>
        `;
        selectedDisplay.style.display = 'block';
        clearBtn.style.display = 'inline-block';
        searchInput.style.display = 'none'; // Hide search bar when item selected? Or just keep it. 
        // Better to hide search or make it clear we have a selection.

        // Trigger manual input toggle (assuming function exists in global scope or we replicate logic)
        if (typeof toggleManualInputs === 'function') {
            toggleManualInputs();
        }
    }

    // Clear selection
    clearBtn.addEventListener('click', function (e) {
        e.preventDefault();
        hiddenInput.value = '';
        selectedDisplay.style.display = 'none';
        clearBtn.style.display = 'none';
        searchInput.style.display = 'block';
        searchInput.value = '';

        if (typeof toggleManualInputs === 'function') {
            toggleManualInputs();
        }
    });

    // Close results if clicking outside
    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
            resultsDiv.style.display = 'none';
        }
    });
});
