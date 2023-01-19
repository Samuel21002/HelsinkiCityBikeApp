document.addEventListener('DOMContentLoaded', () => {
  console.info('Stations page loaded!')

  const render_geoJson = '/stations/render_geojson' // GeoJSON endpoint
  const get_station = '/stations/get_station_info' // Station info endpoint
  const get_station_names = '/stations/get_station_names' // Station names endpoint for the search

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

  /* The Map */
  var map = L.map('id_map').setView([60.22, 24.945831], 11)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)

  /*  Station search 
      Renders all the markers from the returned geoJSON data and adds the necessary click events */
  getJsonData(render_geoJson).then((data) =>
    L.geoJSON(data, {
      pointToLayer: function (geoJsonPoint, latlng) {
        let marker = new L.Marker(latlng, {
          // icon: defaultIcon,
        })

        marker.on('click', function (e) {
          console.log(e)
          get_station_info(e.target.feature.properties.station_id)
          map.flyTo(
            [
              geoJsonPoint.geometry.coordinates[1],
              geoJsonPoint.geometry.coordinates[0],
            ],
            14,
            {
              animate: true,
              easeLinearity: 0.8,
            },
          )
        })

        return marker
      },
      onEachFeature: function (feature, layer) {
        // Popup displays the address
        if (feature.geometry.type === 'Point') {
          layer.bindPopup(
            `${feature.properties.name_fin}, ${feature.properties.name_swe}`,
          )
        }
      },
    }).addTo(map),
  )

  /* Get the station names from the endpoint for the search field */
  const station_names = []
  getJsonData(get_station_names).then((data) =>
    data.forEach((x) => station_names.push(x)),
  )

  /*  The lambda takes in the id of the station.
      - Gets the position of the station on the map,
      - Opens a popup containing the address,
      - Renders the information of a station to the HTML-elements (refreshes the Top-5 list) */
  get_station_info = async (id) => {
    try {
      obj = await getJsonData(`${get_station}/${id}`)
      let latlng = [obj.station.geo_pos_y, obj.station.geo_pos_x]
      map.flyTo(latlng, 14)
      L.popup()
        .setLatLng(latlng)
        .setContent(`${obj.station.name_fin}, ${obj.station.name_swe}`)
        .openOn(map)

      const infoDiv = document.querySelector('.info_ul')
      const table_station_most_pop_ret = document.querySelector(
        '#id_station_dep_most_pop_ret',
      )
      const table_station_most_pop_dep = document.querySelector(
        '#id_station_ret_most_pop_dep',
      )

      while (table_station_most_pop_ret.firstChild) {
        table_station_most_pop_ret.removeChild(
          table_station_most_pop_ret.firstChild,
        )
      }

      obj.station_dep_most_pop_ret.forEach((element) => {
        let tr = document.createElement('tr')
        let td = document.createElement('td')
        td.textContent = `${element.station_count}, ${element.return_station_name}`
        tr.appendChild(td)
        table_station_most_pop_ret.appendChild(tr)
      })

      while (table_station_most_pop_dep.firstChild) {
        table_station_most_pop_dep.removeChild(
          table_station_most_pop_dep.firstChild,
        )
      }

      obj.station_ret_most_pop_dep.forEach((element) => {
        let tr = document.createElement('tr')
        let td = document.createElement('td')
        td.textContent = `${element.station_count}, ${element.departure_station_name}`
        tr.appendChild(td)
        table_station_most_pop_dep.appendChild(tr)
      })

      infoDiv.innerHTML = `<li>Station Name: ${obj.station.name_fin} / ${
        obj.station.name_swe
      }${obj.station.name_eng ? ' / ' + obj.station.name_eng : ''}</li>
      <li>Station Address: ${obj.station.address_fin}${
        obj.station.address_swe ? ', ' + obj.station.address_swe : ' - '
      }</li>
      <li>City: ${obj.station.city_fin}${
        obj.station.city_swe ? ', ' + obj.station.city_swe : ' - '
      }</li>
      <li>Operator: ${obj.station.operator ? obj.station.operator : ' - '}</li>
      <li>Departures from station: ${obj.station_dep_amt}</li>
      <li>Returns to station: ${obj.station_ret_amt}</li>
      <li>Average distance from the station: ${obj.station_dep_dist_avg}</li>
      <li>Average distance to the station: ${obj.station_ret_dist_avg}</li>`
    } catch (error) {
      console.error('Error loading station from the URL!', error)
    }
  }

  /* Finds station matches based on user input in the text field
    Returns the value back to 'displayMatches()' */
  function findMatches(wordToMatch, arr) {
    return arr.filter((station) => {
      const regex = new RegExp(wordToMatch, 'gi')
      return station.name_fin.match(regex) || station.name_swe.match(regex)
    })
  }

  const original_list = document.querySelector('#id_station_list').innerHTML
  /* Gets the value from the findMatches() -function and renders the results as <li> elements to a div */
  function displayMatches() {
    const matchArray = findMatches(this.value, station_names)
    console.log(`Search results: ${matchArray.length}`)
    const input_highlight = matchArray
      .map((station) => {
        const regex = new RegExp(this.value, 'gi')
        const station_fin = station.name_fin.replace(
          regex,
          `<span class="hl">${this.value}</span>`,
        )
        const station_swe = station.name_swe.replace(
          regex,
          `<span class="hl">${this.value}</span>`,
        )
        const address_fin = station.address_fin.replace(
          regex,
          `<span class="hl">${this.value}</span>`,
        )
        const address_swe = station.address_swe.replace(
          regex,
          `<span class="hl">${this.value}</span>`,
        )

        return `
      <li class="pv2">
      <a onclick="get_station_info(${station.station_id});autoFill('${station.name_fin}')" class="link blue lh-title">
          <span class="fw7 underline-hover">${station_fin}, ${station_swe}</span>
          <span class="db black-60">${address_fin}, ${address_swe}</span>
      </a>
      </li>
      `
      })
      .join('')

    if (station_names.length > matchArray.length) {
      station_list.innerHTML = input_highlight
    } else {
      // Resets the div if no textbox input is provided
      station_list.innerHTML = original_list
    }
    console.log($('ul#id_station_list li').length)
  }

  /*  Takes in users station search input and highlights the search results based on what Regex finds */
  const autoFill = (name) => {
    searchInput.value = name
    suggestions.innerHTML = ''
  }

  const searchInput = document.querySelector('#id_search')
  const station_list = document.querySelector('#id_station_list')

  searchInput.addEventListener('change', displayMatches)
  searchInput.addEventListener('keyup', displayMatches)
})
