// Initialize Map
var map = L.map('map', {
    zoomControl: false,
    attributionControl: false
}).setView([31.2304, 121.4737], 5); // Focused on East Asia based on your screenshot

// Dark Theme Tiles
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19
}).addTo(map);

// Example Route (Shanghai to Ningbo)
var routePoints = [
    [31.2304, 121.4737], // Shanghai
    [29.8683, 121.5440]  // Ningbo
];

var polyline = L.polyline(routePoints, {
    color: '#00d4ff',
    weight: 3,
    opacity: 0.8,
    dashArray: '10, 10', // Makes it look like a "moving" path
    lineJoin: 'round'
}).addTo(map);

// Add "Nodes" (Glowing Ports)
var portMarker = L.circleMarker([31.2304, 121.4737], {
    radius: 6,
    fillColor: "#00d4ff",
    color: "#fff",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
}).addTo(map).bindPopup("Shanghai Port - High Congestion");

// Function to simulate dynamic rerouting
function updateRoute(newCoords) {
    polyline.setLatLngs(newCoords);
    map.flyTo(newCoords[0], 6);
}