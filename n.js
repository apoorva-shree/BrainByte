const sidebarLinks = document.querySelectorAll(".sidebar-menu a");
//const sections = document.querySelectorAll("section[id]");
const sections = [
    document.querySelector("#dashboard"),
    document.querySelector("#home"),
    document.querySelector("#donate-section"),
    document.querySelector("#about-us-page")
];


// API Base URL
const API_URL = '/api';

// State Management
let fooditems = [];
let currentFilter = '';
let searchQuery = '';

// DOM Elements
const foodList = document.getElementById('food-list');
const itemForm = document.getElementById('item-form');
const itemModal = document.getElementById('item-modal');
const modalTitle = document.getElementById('modal-title');
const addItemBtn = document.getElementById('add-item-btn');
const themeToggleBtn = document.getElementById('theme-toggle');
const closeBtn = document.querySelector('.close-btn');
const cancelBtn = document.querySelector('.cancel-btn');
//const searchInput = document.getElementById('search-input');
//const categoryFilter = document.getElementById('category-filter');
const notification = document.getElementById('notification');
const loadingSpinner = document.getElementById('loading-spinner');

// Stats Elements
const statTotal = document.getElementById('stat-total');
const statCritical = document.getElementById('stat-critical');
const statWarning = document.getElementById('stat-warning');
const statExpired = document.getElementById('stat-expired');

// Event Listeners
document.addEventListener('DOMContentLoaded', init);
addItemBtn.addEventListener('click', () => openModal());
addItemBtn.addEventListener('click', () => openAddItemDetails());

themeToggleBtn.addEventListener('click', toggleTheme);
closeBtn.addEventListener('click', closeModal);
cancelBtn.addEventListener('click', closeModal);
itemForm.addEventListener('submit', handleFormSubmit);

// Initialize Application
async function init() {
    loadTheme();
    await fetchItems();
    updateStats();
}

// Theme Management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function updateThemeIcon(theme) {
    const icon = themeToggleBtn.querySelector('i');
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

// Fetch Items from API
async function fetchItems() {
    showLoader();
    try {
        const response = await fetch(`${API_URL}/items`);
        const data = await response.json();
        if (data.success) {
            foodItems = data.items.filter(item => !item.consumed);
            renderItems(foodItems);
            updateStats();
        } else {
            showNotification('Error fetching items: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Network error occurred', 'danger');
    } finally {
        hideLoader();
    }
}

// Render Items to UI
function renderItems(items) {
    foodList.innerHTML = '';

    if (items.length === 0) {
        foodList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-shopping-basket"></i>
                <p>${searchQuery || currentFilter ? 'No items match your criteria.' : 'Your inventory is empty. Start adding some food!'}</p>
            </div>
        `;
        return;
    }

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'food-card';
        
        const expiryDateStr = new Date(item.expiryDate).toLocaleDateString();
        const daysLeftText = getDaysLeftText(item.daysUntilExpiry);

        card.innerHTML = `
            <div class="status-indicator ${item.status}"></div>
            <div class="food-card-content">
                <div class="food-header">
                    <h3>${item.name}</h3>
                    <span class="category-badge">${item.category}</span>
                </div>
                <div class="food-info">
                    <p><i class="fas fa-box"></i> ${item.quantity} ${item.unit}</p>
                    <p><i class="fas fa-map-marker-alt"></i> ${item.location}</p>
                    <p class="expiry-text ${item.status === 'critical' || item.status === 'expired' ? 'danger-text' : ''}">
                        <i class="fas fa-calendar-alt"></i> Expires: ${expiryDateStr}
                    </p>
                    <p class="days-left">(${daysLeftText})</p>
                </div>
            </div>
            <div class="food-card-actions">
                <button onclick="consumeItem('${item.id}')" class="btn btn-primary btn-icon" title="Mark as Consumed">
                    <i class="fas fa-check"></i>
                </button>
                <button onclick="openModal('${item.id}')" class="btn btn-secondary btn-icon" title="Edit Item">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="deleteItem('${item.id}')" class="btn btn-danger btn-icon" title="Delete Item">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        foodList.appendChild(card);
    });
}

// Handle Form Submission (Add/Update)
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const itemId = document.getElementById('item-id').value;
    const formData = {
        name: document.getElementById('name').value,
        category: document.getElementById('category').value,
        location: document.getElementById('location').value,
        quantity: document.getElementById('quantity').value,
        unit: document.getElementById('unit').value,
        expiryDate: document.getElementById('expiryDate').value
    };

    try {
        const url = itemId ? `${API_URL}/items/${itemId}` : `${API_URL}/items`;
        const method = itemId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        if (data.success) {
            showNotification(itemId ? 'Item updated!' : 'Item added successfully!');
            closeModal();
            fetchItems();
        } else {
            showNotification('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Failed to save item', 'danger');
    }
}

// Mark Item as Consumed
async function consumeItem(id) {
    try {
        const response = await fetch(`${API_URL}/items/${id}/consume`, { method: 'PATCH' });
        const data = await response.json();
        if (data.success) {
            showNotification('Great! Item marked as consumed.');
            fetchItems();
        }
    } catch (error) {
        showNotification('Action failed', 'danger');
    }
}

// Delete Item
async function deleteItem(id) {
    if (!confirm('Are you sure you want to delete this item?')) return;
    
    try {
        const response = await fetch(`${API_URL}/items/${id}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            showNotification('Item removed from inventory.');
            fetchItems();
        }
    } catch (error) {
        showNotification('Delete failed', 'danger');
    }
}

// Modal Controls
function openModal(id = null) {
    itemForm.reset();
    document.getElementById('item-id').value = '';
    
    if (id) {
        const item = foodItems.find(i => i.id === id);
        if (item) {
            modalTitle.innerText = 'Edit Food Item';
            document.getElementById('item-id').value = item.id;
            document.getElementById('name').value = item.name;
            document.getElementById('category').value = item.category;
            document.getElementById('location').value = item.location;
            document.getElementById('quantity').value = item.quantity;
            document.getElementById('unit').value = item.unit;
            document.getElementById('expiryDate').value = item.expiryDate.split('T')[0];
        }
    } else {
        modalTitle.innerText = 'Add New Food Item';
        // Set default date to 1 week from now
        const nextWeek = new Date();
        nextWeek.setDate(nextWeek.getDate() + 7);
        document.getElementById('expiryDate').value = nextWeek.toISOString().split('T')[0];
    }
    
    itemModal.style.display = 'block';
}

function closeModal() {
    itemModal.style.display = 'none';
}

/* Filter and Search Handlers
function handleFilter(e) {
    currentFilter = e.target.value;
    applyFilters();
}

function handleSearch(e) {
    searchQuery = e.target.value.toLowerCase();
    applyFilters();
}

function applyFilters() {
    let filtered = foodItems;

    if (currentFilter) {
        filtered = filtered.filter(item => item.category === currentFilter);
    }

    if (searchQuery) {
        filtered = filtered.filter(item => 
            item.name.toLowerCase().includes(searchQuery) ||
            item.location.toLowerCase().includes(searchQuery)
        );
    }

    renderItems(filtered);
}*/

// Statistics Update
async function updateStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();
        if (data.success) {
            const { stats } = data;
            statTotal.innerText = stats.total;
            statCritical.innerText = stats.critical;
            statWarning.innerText = stats.warning;
            statExpired.innerText = stats.expired;
        }
    } catch (error) {
        console.error('Stats update failed', error);
    }
}

// Helpers
function getDaysLeftText(days) {
    if (days < 0) return 'Expired';
    if (days === 0) return 'Expires today';
    if (days === 1) return 'Expires tomorrow';
    return `Expires in ${days} days`;
}

function showNotification(message, type = 'success') {
    notification.innerText = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

function showLoader() { loadingSpinner.classList.remove('hidden'); }
function hideLoader() { loadingSpinner.classList.add('hidden'); }

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target == itemModal) closeModal();
}

// Open Add Item Details Modal
function openAddItemDetails() {
    document.getElementById('add-item-details-modal').style.display = 'block';
}

// Close Add Item Details Modal
function closeAddItemDetails() {
    document.getElementById('add-item-details-modal').style.display = 'none';
}

//const sidebarLinks = document.querySelectorAll(".sidebar-menu a");
//const sections = document.querySelectorAll("section[id]");

// Click highlight
sidebarLinks.forEach(link => {
    link.addEventListener("click", () => {
        sidebarLinks.forEach(l => l.classList.remove("active"));
        link.classList.add("active");
    });
});

// Scroll highlight
function activateMenu() {
    let current = "";

    sections.forEach(section => {
        if (!section) return;

        const top = section.offsetTop - 200;
        const height = section.offsetHeight;

        if (
            window.scrollY >= top &&
            window.scrollY < top + height
        ) {
            current = section.id;
        }
    });

    sidebarLinks.forEach(link => {
        link.classList.remove("active");
        if (link.getAttribute("href") === `#${current}`) {
            link.classList.add("active");
        }
    });
}

window.addEventListener("scroll", activateMenu);

document.addEventListener("DOMContentLoaded", () => {
    const sidebarLinks = document.querySelectorAll(".sidebar-menu a");

    const sections = [
        document.getElementById("dashboard"),
        document.getElementById("home"),
        document.getElementById("donate-section"),
        document.getElementById("about-us-page")
    ];

    function activateMenu() {
        let current = "";

        sections.forEach(section => {
            if (!section) return;

            const top = section.offsetTop - 200;
            const height = section.offsetHeight;

            if (window.scrollY >= top && window.scrollY < top + height) {
                current = section.id;
            }
        });

        sidebarLinks.forEach(link => {
            link.classList.remove("active");
            if (link.getAttribute("href") === `#${current}`) {
                link.classList.add("active");
            }
        });
    }

    activateMenu();
    window.addEventListener("scroll", activateMenu);

    sidebarLinks.forEach(link => {
        link.addEventListener("click", () => {
            sidebarLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
        });
    });
});

/*
const sections = [
  document.getElementById("dashboard"),
  document.getElementById("home"),
  document.getElementById("donate-section"),
  document.getElementById("ngo-register-section"),
  document.getElementById("partners-section") // 👈 add this
];

console.log(sections);
*/