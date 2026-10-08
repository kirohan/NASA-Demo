
document.addEventListener('DOMContentLoaded', () => {
    const state = {
        map: null,
        currentCity: 'dhaka',
        currentCoords: { lat: 23.8103, lng: 90.4125 },
        activeMarker: null,
        chartInstance: null,
        layers: { heat: null, vegetation: null, change: null, wards: null },
        cityMetadata: {
            dhaka: { name: 'Dhaka Metropolitan Area', lat: 23.8103, lng: 90.4125, zoom: 12, wardsFile: 'dhaka_wards.geojson' },
            khulna: { name: 'Khulna Resilience Zone', lat: 22.8456, lng: 89.5403, zoom: 13, wardsFile: 'khulna_zones.geojson' },
            phoenix: { name: 'Phoenix Urban Heat Core', lat: 33.4484, lng: -112.0740, zoom: 11 },
            nairobi: { name: 'Nairobi Metropolis', lat: -1.2921, lng: 36.8219, zoom: 12 },
            cairo: { name: 'Cairo Urban Agglomeration', lat: 30.0444, lng: 31.2357, zoom: 11 }
        }
    };

    function initMap() {
        const initial = state.cityMetadata[state.currentCity];
        state.map = L.map('map', { center: [initial.lat, initial.lng], zoom: initial.zoom, zoomControl: false });
        L.control.zoom({ position: 'topright' }).addTo(state.map);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }).addTo(state.map);

        state.map.on('click', (e) => {
            const { lat, lng } = e.latlng;
            state.currentCoords = { lat: parseFloat(lat.toFixed(4)), lng: parseFloat(lng.toFixed(4)) };
            updateCoordinateDisplay(state.currentCoords.lat, state.currentCoords.lng);
            setAnalysisPin(lat, lng, 'Selected Location');
            runAnalysis(state.currentCoords.lat, state.currentCoords.lng, null);
        });

        setupEventListeners();
        loadCity(state.currentCity);
    }

    function setAnalysisPin(lat, lng, title) {
        if (state.activeMarker) state.map.removeLayer(state.activeMarker);
        state.activeMarker = L.circleMarker([lat, lng], { radius: 8, fillColor: '#38bdf8', color: '#ffffff', weight: 2, fillOpacity: 0.9 }).addTo(state.map);
        state.activeMarker.bindPopup(`<strong>${title}</strong><br>Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`).openPopup();
    }

    function updateCoordinateDisplay(lat, lng) {
        document.getElementById('dispLat').textContent = lat.toFixed(3);
        document.getElementById('dispLng').textContent = lng.toFixed(3);
    }

    function setupEventListeners() {
        document.getElementById('citySelect').addEventListener('change', (e) => { state.currentCity = e.target.value; loadCity(state.currentCity); });
        document.getElementById('btnAnalyze').addEventListener('click', () => { runAnalysis(state.currentCoords.lat, state.currentCoords.lng, state.currentCity); });
        document.getElementById('chkHeat').addEventListener('change', (e) => toggleLayer('heat', e.target.checked));
        document.getElementById('chkVegetation').addEventListener('change', (e) => toggleLayer('vegetation', e.target.checked));
        document.getElementById('chkChange').addEventListener('change', (e) => toggleLayer('change', e.target.checked));
        document.getElementById('chkWards').addEventListener('change', (e) => toggleLayer('wards', e.target.checked));
    }

    function toggleLayer(layerKey, isVisible) {
        if (state.layers[layerKey]) {
            if (isVisible) state.map.addLayer(state.layers[layerKey]);
            else state.map.removeLayer(state.layers[layerKey]);
        }
    }

    function loadCity(cityId) {
        const meta = state.cityMetadata[cityId];
        if (!meta) return;
        state.currentCoords = { lat: meta.lat, lng: meta.lng };
        updateCoordinateDisplay(meta.lat, meta.lng);
        document.getElementById('activeAreaTitle').textContent = meta.name;
        state.map.flyTo([meta.lat, meta.lng], meta.zoom, { duration: 1.2 });
        setAnalysisPin(meta.lat, meta.lng, meta.name);
        fetchAndRenderLayers(meta.lat, meta.lng, meta.wardsFile);
        runAnalysis(meta.lat, meta.lng, cityId);
    }

    async function fetchAndRenderLayers(lat, lng, wardsFile) {
        Object.keys(state.layers).forEach(k => { if (state.layers[k]) { state.map.removeLayer(state.layers[k]); state.layers[k] = null; } });
        try {
            const heatRes = await fetch(`/api/layers/heat?lat=${lat}&lng=${lng}&grid_km=10`);
            const heatData = await heatRes.json();
            state.layers.heat = L.geoJSON(heatData.geojson, {
                style: (f) => ({ color: f.properties.fill_color, fillColor: f.properties.fill_color, fillOpacity: f.properties.fill_opacity, weight: 1 }),
                onEachFeature: (f, l) => { l.bindTooltip(`<strong>LST: ${f.properties.temperature_c}°C</strong><br>Risk: ${f.properties.risk_level}`); }
            });
            if (document.getElementById('chkHeat').checked) state.layers.heat.addTo(state.map);

            const vegRes = await fetch(`/api/layers/vegetation?lat=${lat}&lng=${lng}&grid_km=10`);
            const vegData = await vegRes.json();
            state.layers.vegetation = L.geoJSON(vegData.geojson, {
                style: (f) => ({ color: f.properties.fill_color, fillColor: f.properties.fill_color, fillOpacity: f.properties.fill_opacity, weight: 1 }),
                onEachFeature: (f, l) => { l.bindTooltip(`<strong>NDVI: ${f.properties.ndvi}</strong><br>${f.properties.classification}`); }
            });
            if (document.getElementById('chkVegetation').checked) state.layers.vegetation.addTo(state.map);

            const changeRes = await fetch(`/api/layers/urban-change?lat=${lat}&lng=${lng}&grid_km=10`);
            const changeData = await changeRes.json();
            state.layers.change = L.geoJSON(changeData.geojson, {
                style: (f) => ({ color: f.properties.fill_color, fillColor: f.properties.fill_color, fillOpacity: f.properties.fill_opacity, weight: 1 }),
                onEachFeature: (f, l) => { l.bindTooltip(`<strong>${f.properties.change_category}</strong>`); }
            });
            if (document.getElementById('chkChange').checked) state.layers.change.addTo(state.map);

            if (wardsFile) {
                const wardRes = await fetch(`/api/geojson/${wardsFile}`);
                if (wardRes.ok) {
                    const wardData = await wardRes.json();
                    state.layers.wards = L.geoJSON(wardData, {
                        style: { color: '#38bdf8', weight: 2, fillColor: '#0284c7', fillOpacity: 0.15, dashArray: '4, 4' },
                        onEachFeature: (f, l) => {
                            const p = f.properties;
                            l.bindPopup(`<strong>${p.ward_name || p.zone_name}</strong><br>LST: ${p.mean_lst_c}°C<br>NDVI: ${p.mean_ndvi}<br>Risk: ${p.climate_risk_score} (${p.risk_tier})`);
                        }
                    });
                    if (document.getElementById('chkWards').checked) state.layers.wards.addTo(state.map);
                }
            }
        } catch (err) { console.error('Layer error:', err); }
    }

    async function runAnalysis(lat, lng, cityId) {
        try {
            const resp = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat, lng, city_id: cityId, year_start: 2015, year_end: 2025 })
            });
            const data = await resp.json();
            renderMetrics(data);
            renderRiskScore(data.resilience_and_risk);
            renderTrendChart(data.temporal_trends);
            renderRecommendations(data.recommendations);
        } catch (err) { console.error('Analysis error:', err); }
    }

    function renderMetrics(data) {
        const thermal = data.thermal_intelligence;
        const veg = data.vegetation_intelligence;
        const change = data.change_detection.metrics;
        document.getElementById('valTemperature').innerHTML = `${thermal.mean_temperature_c} <small>°C</small>`;
        document.getElementById('valHeatRisk').innerHTML = `<span class="badge ${thermal.overall_risk_level === 'Extreme' ? 'badge-extreme' : 'badge-high'}">${thermal.overall_risk_level} Thermal Stress (+${thermal.uhi_intensity_c}°C UHI)</span>`;
        document.getElementById('valNdvi').innerHTML = `${veg.mean_ndvi} <small>NDVI</small>`;
        document.getElementById('valGreenCoverage').innerHTML = `<span class="badge badge-warning">Canopy Deficit: ${veg.vegetation_deficit_pct}%</span>`;
        document.getElementById('valUrbanChange').innerHTML = `${change.built_up_change_pct > 0 ? '+' : ''}${change.built_up_change_pct} <small>%</small>`;
        document.getElementById('valCanopyLoss').innerHTML = `<span class="badge badge-danger">Canopy: ${change.vegetation_change_pct > 0 ? '+' : ''}${change.vegetation_change_pct}%</span>`;
    }

    function renderRiskScore(riskData) {
        const score = Math.round(riskData.climate_risk_score);
        document.getElementById('riskScoreVal').textContent = score;
        const circle = document.getElementById('scoreCircle');
        const color = score >= 80 ? '#ef4444' : (score >= 60 ? '#f97316' : '#38bdf8');
        circle.style.borderColor = color;
        circle.style.boxShadow = `0 0 16px ${color}66`;
        document.getElementById('riskTierBadge').innerHTML = `<span class="badge ${score >= 80 ? 'badge-extreme' : 'badge-high'}">Risk Level: ${riskData.risk_level}</span>`;
        const listElem = document.getElementById('riskDriversList');
        listElem.innerHTML = '';
        riskData.reasons.forEach(r => { const li = document.createElement('li'); li.textContent = r; listElem.appendChild(li); });
    }

    function renderTrendChart(trends) {
        const ctx = document.getElementById('trendChart').getContext('2d');
        if (state.chartInstance) state.chartInstance.destroy();
        state.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trends.map(t => t.year),
                datasets: [
                    { label: 'Mean LST (°C)', data: trends.map(t => t.mean_lst_c), borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', tension: 0.35, yAxisID: 'yLST' },
                    { label: 'Green (%)', data: trends.map(t => t.green_space_area_pct), borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', tension: 0.35, yAxisID: 'yGreen' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b', font: { size: 9 } } },
                    yLST: { position: 'left', ticks: { color: '#f87171', font: { size: 9 } } },
                    yGreen: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: '#34d399', font: { size: 9 } } }
                }
            }
        });
    }

    function renderRecommendations(recs) {
        const container = document.getElementById('recList');
        container.innerHTML = '';
        recs.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'rec-card';
            const items = rec.action_items.map(i => `<li><i class="fa-solid fa-chevron-right"></i> ${i}</li>`).join('');
            card.innerHTML = `
                <div class="rec-header">
                    <div class="rec-title">${rec.title}</div>
                    <span class="rec-priority priority-${rec.priority.toLowerCase()}">${rec.priority} Priority</span>
                </div>
                <div class="rec-impact"><i class="fa-solid fa-bolt"></i> ${rec.estimated_impact}</div>
                <ul class="rec-items">${items}</ul>
                <div class="rec-eo-metric"><strong>Satellite Metric:</strong> ${rec.satellite_monitoring_metric}</div>
            `;
            container.appendChild(card);
        });
    }

    initMap();
});
