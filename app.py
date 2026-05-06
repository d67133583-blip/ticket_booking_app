"""
TicketHub Backend - Flask Application
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
import os
from functools import wraps

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Configure app
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Sample event database
EVENTS_DB = [
    {
        "id": 1,
        "title": "The Midnight Sessions - Live Concert",
        "category": "concert",
        "date": "2024-06-15",
        "time": "19:00",
        "venue": "Grand Arena Stadium",
        "price": 89,
        "icon": "🎸",
        "description": "Experience an unforgettable night with world-class musicians performing their greatest hits.",
        "capacity": 5000,
        "available_tickets": 1250
    },
    {
        "id": 2,
        "title": "Championship Final - Basketball Tournament",
        "category": "sports",
        "date": "2024-06-20",
        "time": "18:30",
        "venue": "Metropolitan Sports Center",
        "price": 65,
        "icon": "🏀",
        "description": "Watch the most exciting basketball game of the season with top athletes competing for glory.",
        "capacity": 8000,
        "available_tickets": 2100
    },
    {
        "id": 3,
        "title": "Shakespeare's Hamlet - Classic Theater",
        "category": "theater",
        "date": "2024-06-22",
        "time": "20:00",
        "venue": "Royal Theater House",
        "price": 75,
        "icon": "🎭",
        "description": "A timeless masterpiece performed by award-winning actors in an intimate theater setting.",
        "capacity": 1200,
        "available_tickets": 340
    },
    {
        "id": 4,
        "title": "Tech Summit 2024 - Innovation Conference",
        "category": "conference",
        "date": "2024-07-01",
        "time": "09:00",
        "venue": "Convention Center",
        "price": 199,
        "icon": "💼",
        "description": "Join industry leaders discussing the latest trends in technology, AI, and digital transformation.",
        "capacity": 3000,
        "available_tickets": 850
    },
    {
        "id": 5,
        "title": "Summer Music Festival",
        "category": "concert",
        "date": "2024-07-10",
        "time": "16:00",
        "venue": "Central Park Amphitheater",
        "price": 45,
        "icon": "🎵",
        "description": "A full-day music festival featuring diverse artists and amazing performances.",
        "capacity": 10000,
        "available_tickets": 3500
    },
    {
        "id": 6,
        "title": "Tennis Masters Open",
        "category": "sports",
        "date": "2024-07-15",
        "time": "14:00",
        "venue": "Tennis Complex",
        "price": 95,
        "icon": "🎾",
        "description": "Watch world-class tennis players compete in this prestigious international tournament.",
        "capacity": 4000,
        "available_tickets": 1100
    }
]

# In-memory bookings storage
BOOKINGS_DB = []

# Utility function for HTML escaping
def escape_html(text):
    """Properly escape HTML characters"""
    if not isinstance(text, str):
        text = str(text)
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)


# FRONTEND ROUTES
@app.route('/', methods=['GET'])
def index():
    """Serve the main application - Returns HTML inline"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TicketHub - Book Your Events</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .logo span {
            font-size: 32px;
        }

        .nav-links {
            display: flex;
            gap: 30px;
        }

        .nav-links a {
            text-decoration: none;
            color: #333;
            font-weight: 500;
            transition: color 0.3s;
        }

        .nav-links a:hover {
            color: #667eea;
        }

        .search-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .search-container {
            display: flex;
            gap: 10px;
        }

        .search-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .filter-btn, .search-btn {
            padding: 12px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }

        .search-btn:hover, .filter-btn:hover {
            background: #764ba2;
        }

        .search-result-info {
            margin-top: 15px;
            padding: 10px 15px;
            background: #f5f5f5;
            border-radius: 6px;
            color: #666;
            font-size: 14px;
        }

        .api-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 100;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4CAF50;
        }

        .status-dot.offline {
            background: #f44336;
        }

        .filters {
            display: flex;
            gap: 15px;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        .filter-chip {
            padding: 8px 15px;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }

        .filter-chip:hover {
            background: #e0e0e0;
        }

        .filter-chip.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .events-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .event-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }

        .event-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }

        .event-image {
            width: 100%;
            height: 180px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 48px;
        }

        .event-content {
            padding: 20px;
        }

        .event-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }

        .event-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 12px;
            font-size: 14px;
            color: #666;
            flex-wrap: wrap;
        }

        .event-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .event-description {
            font-size: 14px;
            color: #777;
            margin-bottom: 15px;
            line-height: 1.5;
        }

        .event-price {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
        }

        .event-tickets {
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
        }

        .book-btn {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }

        .book-btn:hover {
            background: #764ba2;
        }

        .book-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: white;
        }

        .empty-state h2 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: white;
        }

        .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .modal-header {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }

        .modal-body {
            margin-bottom: 20px;
            color: #666;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }

        .form-input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .modal-buttons {
            display: flex;
            gap: 10px;
        }

        .modal-btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }

        .confirm-btn {
            background: #667eea;
            color: white;
        }

        .confirm-btn:hover {
            background: #764ba2;
        }

        .cancel-btn {
            background: #f0f0f0;
            color: #333;
        }

        .cancel-btn:hover {
            background: #e0e0e0;
        }

        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }

        .api-note {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            padding: 12px 15px;
            border-radius: 6px;
            margin-top: 15px;
            font-size: 13px;
        }

        .api-note a {
            color: #fff;
            text-decoration: underline;
        }

        .success-message {
            background: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            display: none;
        }

        .success-message.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="api-status" id="apiStatus">
        <div class="status-dot"></div>
        <span id="statusText">API: Online ✓</span>
    </div>

    <div class="container">
        <header>
            <div class="logo">
                <span>🎫</span>
                TicketHub
            </div>
            <nav class="nav-links">
                <a href="#home">Home</a>
                <a href="#events">Events</a>
                <a href="#bookings" onclick="loadUserBookings()">My Bookings</a>
                <a href="#contact">Contact</a>
            </nav>
        </header>

        <div class="search-section">
            <h2 style="margin-bottom: 20px; color: #333;">Find Your Perfect Event</h2>
            <div class="search-container">
                <input 
                    type="text" 
                    class="search-input" 
                    id="searchInput" 
                    placeholder="Search events by name, artist, or venue..."
                >
                <button class="search-btn" onclick="searchEvents()">Search</button>
                <button class="filter-btn" onclick="toggleFilters()">Filters</button>
            </div>

            <div id="searchResultInfo"></div>

            <div class="filters">
                <div class="filter-chip active" onclick="filterByCategory(this, 'all')">All Events</div>
                <div class="filter-chip" onclick="filterByCategory(this, 'concert')">🎵 Concerts</div>
                <div class="filter-chip" onclick="filterByCategory(this, 'sports')">🏀 Sports</div>
                <div class="filter-chip" onclick="filterByCategory(this, 'theater')">🎭 Theater</div>
                <div class="filter-chip" onclick="filterByCategory(this, 'conference')">💼 Conferences</div>
            </div>

            <div class="api-note">
            </div>
        </div>

        <div class="events-grid" id="eventsGrid">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading events...</p>
            </div>
        </div>

        <div class="empty-state" id="emptyState" style="display: none;">
            <h2>No events found</h2>
            <p>Try adjusting your search or filters</p>
        </div>

        <div class="modal" id="bookingModal">
            <div class="modal-content">
                <div class="modal-header">Book Event Ticket</div>
                <div id="successMessage" class="success-message"></div>
                <div class="modal-body">
                    <div id="modalEventDetails"></div>

                    <div class="form-group">
                        <label class="form-label">Your Name</label>
                        <input type="text" class="form-input" id="customerName" placeholder="Enter your full name">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Email Address</label>
                        <input type="email" class="form-input" id="customerEmail" placeholder="Enter your email">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Number of Tickets</label>
                        <input type="number" class="form-input" id="ticketQuantity" min="1" max="10" value="1" placeholder="Number of tickets">
                    </div>

                    <div class="form-group">
                        <strong>Total Price: $<span id="modalTotalPrice">0</span></strong>
                    </div>
                </div>
                <div class="modal-buttons">
                    <button class="modal-btn confirm-btn" onclick="confirmBooking()">Confirm Booking</button>
                    <button class="modal-btn cancel-btn" onclick="closeModal()">Cancel</button>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>&copy; 2024 TicketHub. Backend: Python Flask | API: <span id="apiUrl">http://localhost:5000/api</span></p>
        </div>
    </div>

    <script>
        const API_BASE_URL = '/api';
        let allEvents = [];
        let filteredEvents = [];
        let currentCategory = 'all';
        let selectedEvent = null;

        window.addEventListener('load', () => {
            loadAllEvents();
        });

        async function loadAllEvents() {
            try {
                const response = await fetch(`${API_BASE_URL}/events`);
                const data = await response.json();

                if (data.success) {
                    allEvents = data.data;
                    filteredEvents = [...allEvents];
                    renderEvents();
                    document.getElementById('apiStatus').style.display = 'flex';
                } else {
                    showError('Failed to load events');
                }
            } catch (error) {
                console.error('Error loading events:', error);
                showError('Could not connect to API');
            }
        }

        function renderEvents() {
            const grid = document.getElementById('eventsGrid');
            const emptyState = document.getElementById('emptyState');

            if (filteredEvents.length === 0) {
                grid.style.display = 'none';
                emptyState.style.display = 'block';
            } else {
                grid.style.display = 'grid';
                emptyState.style.display = 'none';
                grid.innerHTML = filteredEvents.map(event => `
                    <div class="event-card">
                        <div class="event-image">${event.icon}</div>
                        <div class="event-content">
                            <div class="event-title">${escapeHtml(event.title)}</div>
                            <div class="event-meta">
                                <span>📅 ${event.date}</span>
                                <span>🕐 ${event.time}</span>
                            </div>
                            <div class="event-meta">
                                <span>📍 ${escapeHtml(event.venue)}</span>
                            </div>
                            <div class="event-description">${escapeHtml(event.description)}</div>
                            <div class="event-price">$${event.price}</div>
                            <div class="event-tickets">📊 ${event.available_tickets} tickets available</div>
                            <button class="book-btn" onclick="openBookingModal(${event.id})">Book Now</button>
                        </div>
                    </div>
                `).join('');
            }
        }

        function filterByCategory(chip, category) {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentCategory = category;

            if (category === 'all') {
                filteredEvents = [...allEvents];
            } else {
                filteredEvents = allEvents.filter(e => e.category === category);
            }

            clearSearchInfo();
            renderEvents();
        }

        async function searchEvents() {
            const query = document.getElementById('searchInput').value;

            if (query === '') {
                filteredEvents = currentCategory === 'all'
                    ? [...allEvents]
                    : allEvents.filter(e => e.category === currentCategory);
                clearSearchInfo();
                renderEvents();
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.success) {
                    filteredEvents = data.data;
                    const resultInfo = document.getElementById('searchResultInfo');
                    resultInfo.innerHTML = `<strong>Search results for:</strong> "${query}" - Found ${filteredEvents.length} event(s)`;
                    renderEvents();
                } else {
                    showError(data.error || 'Search failed');
                }
            } catch (error) {
                console.error('Error searching events:', error);
                showError('Could not perform search');
            }
        }

        function clearSearchInfo() {
            document.getElementById('searchResultInfo').innerHTML = '';
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        function openBookingModal(eventId) {
            selectedEvent = allEvents.find(e => e.id === eventId);
            if (selectedEvent) {
                const details = `
                    <div>
                        <strong>${escapeHtml(selectedEvent.title)}</strong>
                        <p style="margin-top: 10px; color: #777;">
                            ${escapeHtml(selectedEvent.date)} at ${selectedEvent.time}<br>
                            ${escapeHtml(selectedEvent.venue)}
                        </p>
                    </div>
                `;
                document.getElementById('modalEventDetails').innerHTML = details;
                document.getElementById('ticketQuantity').max = selectedEvent.available_tickets;
                document.getElementById('ticketQuantity').value = 1;
                updateTotalPrice();
                document.getElementById('bookingModal').classList.add('active');
            }
        }

        function closeModal() {
            document.getElementById('bookingModal').classList.remove('active');
        }

        function updateTotalPrice() {
            const quantity = parseInt(document.getElementById('ticketQuantity').value) || 1;
            const total = selectedEvent.price * quantity;
            document.getElementById('modalTotalPrice').textContent = total;
        }

        async function confirmBooking() {
            const name = document.getElementById('customerName').value;
            const email = document.getElementById('customerEmail').value;
            const quantity = parseInt(document.getElementById('ticketQuantity').value);

            if (!name || !email || !quantity) {
                alert('Please fill in all fields');
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/booking`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        event_id: selectedEvent.id,
                        customer_name: name,
                        customer_email: email,
                        quantity: quantity
                    })
                });

                const data = await response.json();

                if (data.success) {
                    const successMsg = document.getElementById('successMessage');
                    successMsg.innerHTML = `✅ Booking confirmed! ID: ${data.data.booking_id}`;
                    successMsg.classList.add('show');
                    setTimeout(() => {
                        closeModal();
                        loadAllEvents();
                    }, 2000);
                } else {
                    alert('❌ Booking failed: ' + data.error);
                }
            } catch (error) {
                console.error('Error confirming booking:', error);
                alert('Could not process booking');
            }
        }

        async function loadUserBookings() {
            const email = prompt('Enter your email to view bookings:');
            if (email) {
                try {
                    const response = await fetch(`${API_BASE_URL}/bookings?email=${encodeURIComponent(email)}`);
                    const data = await response.json();

                    if (data.success) {
                        if (data.data.length === 0) {
                            alert('No bookings found for this email');
                        } else {
                            let message = `You have ${data.data.length} booking(s):\\n\\n`;
                            data.data.forEach((b, i) => {
                                message += `${i + 1}. ${b.event_title}\\n   ID: ${b.booking_id}\\n   Tickets: ${b.quantity}\\n   Total: $${b.total_price}\\n\\n`;
                            });
                            alert(message);
                        }
                    }
                } catch (error) {
                    console.error('Error loading bookings:', error);
                    alert('Could not load bookings');
                }
            }
        }

        function showError(message) {
            alert('Error: ' + message);
        }

        function toggleFilters() {
            alert('Advanced filters coming soon!');
        }

        document.getElementById('searchInput').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                searchEvents();
            }
        });

        document.getElementById('ticketQuantity').addEventListener('change', updateTotalPrice);

        document.getElementById('bookingModal').addEventListener('click', function (e) {
            if (e.target === this) {
                closeModal();
            }
        });
    </script>
</body>
</html>
"""
    return html_content


# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TicketHub Backend",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/events', methods=['GET'])
def get_all_events():
    """Get all events with optional category filter"""
    category = request.args.get('category', '').lower()
    
    events = EVENTS_DB
    
    if category and category != 'all':
        events = [e for e in events if e['category'] == category]
    
    return jsonify({
        "success": True,
        "count": len(events),
        "data": events
    }), 200


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by ID"""
    event = next((e for e in EVENTS_DB if e['id'] == event_id), None)
    
    if not event:
        return jsonify({
            "success": False,
            "error": "Event not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": event
    }), 200


@app.route('/api/search', methods=['GET'])
def search_events():
   
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Search query is required"
        }), 400
    
    # Filter events based on search query
    results = [
        e for e in EVENTS_DB
        if query in e['title'].lower() 
        or query in e['venue'].lower()
        or query in e['description'].lower()
    ]
    
    
    search_message = f'Search results for: "{query}" - Found {len(results)} event(s)'
    
    response = {
        "success": True,
        "search_query": query,  
        "search_message": search_message, 
        "results_count": len(results),
        "data": results,
        "note": "This endpoint contains a search_message field"
    }
    
    return jsonify(response), 200


@app.route('/api/search/safe', methods=['GET'])
def search_events_safe():
    
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Search query is required"
        }), 400
    
    # Filter events based on search query
    results = [
        e for e in EVENTS_DB
        if query in e['title'].lower() 
        or query in e['venue'].lower()
        or query in e['description'].lower()
    ]
    
    # SECURE CODE: Properly escape user input
    safe_query = escape_html(query)
    search_message = f'Search results for: "{safe_query}" - Found {len(results)} event(s)'
    
    response = {
        "success": True,
        "search_query": safe_query,  # SAFE: User input is properly escaped
        "search_message": search_message,  # SAFE: Message uses escaped input
        "results_count": len(results),
        "data": results,
        "note": "This"
    }
    
    return jsonify(response), 200


@app.route('/api/filter', methods=['POST'])
def filter_events():
    """Filter events by multiple criteria"""
    try:
        filters = request.get_json()
        
        filtered = EVENTS_DB
        
        # Filter by category
        if filters.get('category') and filters['category'] != 'all':
            filtered = [e for e in filtered if e['category'] == filters['category']]
        
        # Filter by price range
        if filters.get('min_price') is not None:
            filtered = [e for e in filtered if e['price'] >= filters['min_price']]
        
        if filters.get('max_price') is not None:
            filtered = [e for e in filtered if e['price'] <= filters['max_price']]
        
        # Filter by date range
        if filters.get('start_date'):
            filtered = [e for e in filtered if e['date'] >= filters['start_date']]
        
        if filters.get('end_date'):
            filtered = [e for e in filtered if e['date'] <= filters['end_date']]
        
        return jsonify({
            "success": True,
            "count": len(filtered),
            "data": filtered
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/booking', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_id', 'quantity', 'customer_email']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "error": "Missing required fields: " + ", ".join(required_fields)
            }), 400
        
        # Find event
        event = next((e for e in EVENTS_DB if e['id'] == data['event_id']), None)
        if not event:
            return jsonify({
                "success": False,
                "error": "Event not found"
            }), 404
        
        # Check availability
        if data['quantity'] > event['available_tickets']:
            return jsonify({
                "success": False,
                "error": f"Only {event['available_tickets']} tickets available"
            }), 400
        
        # Create booking
        booking = {
            "booking_id": f"BK{len(BOOKINGS_DB) + 1001}",
            "event_id": data['event_id'],
            "event_title": event['title'],
            "quantity": data['quantity'],
            "total_price": event['price'] * data['quantity'],
            "customer_email": data['customer_email'],
            "customer_name": data.get('customer_name', 'Guest'),
            "booking_date": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        # Update available tickets
        event['available_tickets'] -= data['quantity']
        
        # Store booking
        BOOKINGS_DB.append(booking)
        
        return jsonify({
            "success": True,
            "message": "Booking created successfully",
            "data": booking
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings (for demo purposes)"""
    email = request.args.get('email', '')
    
    bookings = BOOKINGS_DB
    if email:
        bookings = [b for b in bookings if b['customer_email'] == email]
    
    return jsonify({
        "success": True,
        "count": len(bookings),
        "data": bookings
    }), 200


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all event categories"""
    categories = set(e['category'] for e in EVENTS_DB)
    
    return jsonify({
        "success": True,
        "data": sorted(list(categories))
    }), 200


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get booking statistics"""
    total_events = len(EVENTS_DB)
    total_bookings = len(BOOKINGS_DB)
    total_revenue = sum(b['total_price'] for b in BOOKINGS_DB)
    
    return jsonify({
        "success": True,
        "data": {
            "total_events": total_events,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            "bookings_by_category": {
                cat: sum(1 for b in BOOKINGS_DB 
                        if next((e for e in EVENTS_DB if e['id'] == b['event_id']), {}).get('category') == cat)
                for cat in set(e['category'] for e in EVENTS_DB)
            }
        }
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({
        "success": False,
        "error": "Access forbidden"
    }), 403


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║        TicketHub Backend - Flask Application              ║
    ║                                                           ║
    ║  🎫 Server running at: http://localhost:5000             ║
    ║  🌐 Frontend: http://localhost:5000                       ║
    ║  📚 API: http://localhost:5000/api/health                ║
    ║                                                           ║
    ║          ║
    ║                                                           ║
    ║  Quick Links:                                            ║
    ║  - GET  /api/events              (Get all events)        ║
    ║  - GET  /api/search?q=<query>    (Search)   ║
    ║  - GET  /api/search/safe?q=<q>   (Search - SAFE)         ║
    ║  - POST /api/booking             (Create booking)        ║
    ║  - GET  /api/bookings            (View bookings)         ║
    ║  - GET  /api/categories          (Get categories)        ║
    ║  - GET  /api/statistics          (Get statistics)        ║
    ║  - GET  /api/health              (Health check)          ║
    ║                                                           ║
    ║  Ctrl+C to stop server                                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5001)