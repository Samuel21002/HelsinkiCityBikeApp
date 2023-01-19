const get_station_geoJson = '/stations/render_geojson';

/* DateTime -range picker */
$(function() {
    $('input[name="daterange"]').daterangepicker({
    opens: 'left',
    "startDate": "01/01/2020",
    "endDate": "12/30/2022",
    }, function(start, end, label) {
    console.log("A new date selection was made: " + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD'));
    });
});

/* Map */
var map = L.map('id_map').setView([60.22, 24.945831], 11);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

/*  For fetching JSONResponses 
    Takes in the provided url and returns as parsed JSON */
async function getJsonData(url) {
    try {
    const response = await fetch(url)
    const data = await response.json()
    return JSON.parse(data)
    } catch (e) {
    console.error('Error loading JSONresponse from the URL!')
    console.error(e)
    }
}

/* Generates the geoJSON map.
    Imports stations from the Django back-end endpoint using fetch, sets a style, renders the markers on the map,
    creates click events and popups */
getJsonData(get_station_geoJson).then(data => L.geoJSON(data, {

    pointToLayer: function(geoJsonPoint, latlng) {  
        let marker = new L.Marker(latlng, {
            
        });
        
        marker.on('click', function(e) {     // OnClick event locks onto new coordinates and gets the info from the backend
            map.flyTo([geoJsonPoint.geometry.coordinates[1], geoJsonPoint.geometry.coordinates[0]], 14, {
                animate: true,
                easeLinearity: 0.8
            })
        });

        return marker
    },
    onEachFeature: function(feature, layer) {   // Popups on click displays the address
        if(feature.geometry.type === 'Point') {
            layer.bindPopup(`${feature.properties.name_fin}, ${feature.properties.name_swe}`)
            
        }
    }
}).addTo(map));


/* Front-end form validation. If invalid search input is provided, error is rendered to the output element */
const error = document.getElementById('errors')
const form = document.querySelector('#id_journey_form')
form.onchange = function() { 

    const journey_dep_station = document.getElementById('id_departure')
    const journey_ret_station = document.getElementById('id_return')
    const distance = document.getElementsByName('distance')
    const button = document.getElementById('id_submit')
    const duration = document.getElementsByName('duration')

    const conditionsArray = [
        Boolean(!journey_dep_station.checked && !journey_ret_station.checked),
        Boolean(distance[0].value < 10),
        Boolean(Number(distance[1].value) < Number(distance[0].value)),
        Boolean(duration[0].value < 10), 
        Boolean(Number(duration[1].value) < Number(duration[0].value))
    ]
    
    if (conditionsArray.includes(true)) {
        error.innerHTML = "Invalid input, check your values!"
        button.setAttribute("disabled", "disabled");

    } else {
        error.innerHTML = ""
        button.removeAttribute("disabled");
    }
}

/*  Gets the essential journey info and renders an arrow from the departure to the return station.  
    Takes in a journey id and gets the data from the backend using fetch. 
    The closure takes in the map object from the page and adds the arrow layer to it. 
    If a previous arrow layer is found, it gets replaced with a new journey.
*/
let layer;  // Updates the current journey leaflet layer with a new one
function get_journey(id) {   
    
    // Closure-function for creating a new layer on the map containing the journey
    function createGeoJSONLayer(map) {
        
        return function(geoJSON) {
            // If the layer already exists, remove it from the map
            if (layer) {
                map.removeLayer(layer);
                layer = null
            }
            // If not, create the new layer from the geoJSON data
            if (geoJSON) {
                layer = L.geoJSON(geoJSON, {
                    style : {
                        "color": "#00aa22",
                        "weight": 6,
                        "opacity": 0.85
                    },
                    onEachFeature: function(feature, layer) {   // Popups on click displays the address
                        if(feature.geometry.type === 'LineString') {
                            layer.bindPopup(feature.properties.stations)
                            map.fitBounds(feature.geometry.bounds)
                        }
                        
                        layer.on('click', function(){
                            map.fitBounds(feature.geometry.bounds)
                        })
                        
                    },
                    arrowheads: {
                        frequency: '30px', 
                        size: '14px'
                    }
                }).addTo(map);
            }
        }
    }
    const endpoint = `/journeys/get_journey_info/${id}`
    const updateGeoJSONLayer = createGeoJSONLayer(map);

    fetch(endpoint)
    .then((response) => response.json())
    .then((geoJSON) => updateGeoJSONLayer(JSON.parse(geoJSON)))
    .catch((error) => console.error(error));
}
