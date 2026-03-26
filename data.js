// data.js - Shared Data and Logic
const houses = [
    { 
        id: 101, 
        title: "Modern Glass Villa", 
        price: "$500,000", 
        style: "Modern", 
        location: "Seattle, WA", 
        image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800",
        desc: "A sleek home with floor-to-ceiling windows and an open floor plan." 
    },
    { 
        id: 102, 
        title: "Historic Victorian", 
        price: "$750,000", 
        style: "Victorian", 
        location: "San Francisco, CA", 
        image: "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800",
        desc: "Classic Victorian exterior with original architectural details." 
    },
    { 
        id: 103, 
        title: "Rustic Farmhouse", 
        price: "$400,000", 
        style: "Farm", 
        location: "Starkville, MS", 
        image: "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=800", // Actual Farmhouse House
        desc: "Traditional farmhouse with a large porch and 5 acres of land." 
    },
    { 
        id: 104, 
        title: "Mediterranean Retreat", 
        price: "$900,000", 
        style: "Mediterranean", 
        location: "Boca Raton, FL", 
        image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800",
        desc: "Luxury living with stucco walls and a private pool area." 
    },
    { 
        id: 105, 
        title: "Classic Colonial", 
        price: "$600,000", 
        style: "Colonial", 
        location: "Boston, MA", 
        image: "https://images.unsplash.com/photo-1576941089067-2de3c901e126?auto=format&fit=crop&w=800", // Reliable Colonial House link
        desc: "Symmetrical colonial design with a beautiful brick facade." 
    }
];

function updateCartUI() {
    const cart = JSON.parse(localStorage.getItem('homeZappCart')) || [];
    const countElement = document.getElementById('cart-count');
    if (countElement) countElement.innerText = cart.length;
}

window.addEventListener('DOMContentLoaded', updateCartUI);