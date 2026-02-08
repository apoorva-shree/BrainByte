// FastAPI Configuration
const API_URL = "http://localhost:8000/api";

// DOM Elements
const donationForm = document.getElementById('donation-form');
const ngoForm = document.getElementById('ngo-register-form');
const itemForm = document.getElementById('item-form');
const itemModal = document.getElementById('item-modal');
const addItemBtn = document.getElementById('add-item-btn');
const closeBtn = document.querySelector('.close-btn');
const cancelBtn = document.querySelector('.cancel-btn');
const notification = document.getElementById('notification');

// --- Notification Helper ---
function showNotification(message, isError = false) {
    notification.textContent = message;
    notification.className = `notification ${isError ? 'error' : ''}`;
    notification.classList.remove('hidden');
    setTimeout(() => notification.classList.add('hidden'), 3000);
}

// --- Dashboard Stats ---
async function updateDashboard() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();
        if (data.success) {
            const stats = data.stats;
            document.getElementById('stat-total').textContent = stats.total;
            document.getElementById('stat-critical').textContent = stats.critical;
            document.getElementById('stat-warning').textContent = stats.warning;
            document.getElementById('stat-expired').textContent = stats.expired;
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// --- Item Submission (Inventory) ---
if (itemForm) {
    itemForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('item-id').value;
        const itemData = {
            name: document.getElementById('name').value,
            category: document.getElementById('category').value,
            location: document.getElementById('location').value || "Not specified",
            quantity: parseFloat(document.getElementById('quantity').value),
            unit: document.getElementById('unit').value || "units",
            expiryDate: document.getElementById('expiryDate').value
        };

        try {
            let response;
            if (id) {
                response = await fetch(`${API_URL}/items/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(itemData)
                });
            } else {
                response = await fetch(`${API_URL}/items`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(itemData)
                });
            }

            const data = await response.json();
            if (data.success) {
                showNotification(id ? 'Item updated!' : 'Item added!');
                itemModal.style.display = 'none';
                itemForm.reset();
                updateDashboard();
            } else {
                showNotification('Error saving item', true);
            }
        } catch (error) {
            console.error('Error saving item:', error);
            showNotification('Error connecting to server', true);
        }
    });
}

// --- Donation Submission ---
if (donationForm) {
    donationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = donationForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';

        const donationData = {
            donorName: donationForm.querySelectorAll('input')[0].value,
            contact: donationForm.querySelectorAll('input')[1].value,
            donorType: donationForm.querySelectorAll('select')[0].value,
            foodType: donationForm.querySelectorAll('select')[1].value,
            description: donationForm.querySelector('textarea').value,
            quantity: parseInt(donationForm.querySelector('input[type="number"]').value),
            location: donationForm.querySelectorAll('textarea')[1].value,
            expiryTime: donationForm.querySelectorAll('select')[2].value
        };

        try {
            const response = await fetch(`${API_URL}/donations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(donationData)
            });
            const data = await response.json();
            if (data.success) {
                showNotification('Donation submitted successfully!');
                donationForm.reset();
            } else {
                showNotification('Error submitting donation', true);
            }
        } catch (error) {
            console.error(error);
            showNotification('Error connecting to server', true);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Donation';
        }
    });
}

// --- NGO Registration ---
if (ngoForm) {
    ngoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = ngoForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        const ngoData = {
            name: document.getElementById('ngo-name').value,
            contactPerson: document.getElementById('contact-person').value,
            contact: document.getElementById('contact-number').value,
            address: document.getElementById('address').value,
            capacity: parseInt(document.getElementById('capacity').value)
        };

        try {
            const response = await fetch(`${API_URL}/ngos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ngoData)
            });
            const data = await response.json();
            if (data.success) {
                showNotification('NGO Registered successfully!');
                ngoForm.reset();
            } else {
                showNotification('Error registering NGO', true);
            }
        } catch (error) {
            console.error(error);
            showNotification('Error connecting to server', true);
        } finally {
            submitBtn.disabled = false;
        }
    });
}

// --- Modal Logic ---
if (addItemBtn) {
    addItemBtn.onclick = () => {
        document.getElementById('modal-title').textContent = 'Add New Food Item';
        document.getElementById('item-id').value = '';
        itemForm.reset();
        itemModal.style.display = 'block';
    };
}

if (closeBtn) closeBtn.onclick = () => itemModal.style.display = 'none';
if (cancelBtn) cancelBtn.onclick = () => itemModal.style.display = 'none';

window.onclick = (event) => {
    if (event.target == itemModal) itemModal.style.display = 'none';
};

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
});
