
document.addEventListener('DOMContentLoaded', () => {
    const state = {
        map: null,
        currentCity: 'khulna',
        currentYear: 2026,
        currentCoords: { lat: 22.8456, lng: 89.5403 },
        activeMarker: null,
        chartInstance: null,
        activeBasemap: 'googleHybrid',
        baseTileLayers: {},
        activeEnvLayer: 'heat',
        opacity: 0.45,
        isPlaying: false,
        playInterval: null,
        layers: { smoothHeat: null, vegetation: null, change: null, wards: null },
        cityMetadata: {
            khulna: { name: 'Khulna Resilience Zone', lat: 22.8456, lng: 89.5403, zoom: 13, wardsFile: 'khulna_zones.geojson' },
            dhaka: { name: 'Dhaka Metropolitan Area', lat: 23.8103, lng: 90.4125, zoom: 12, wardsFile: 'dhaka_wards.geojson' },
            phoenix: { name: 'Phoenix Urban Heat Core', lat: 33.4484, lng: -112.0740, zoom: 11 },
            nairobi: { name: 'Nairobi Metropolis', lat: -1.2921, lng: 36.8219, zoom: 12 },
            cairo: { name: 'Cairo Urban Agglomeration', lat: 30.0444, lng: 31.2357, zoom: 11 }
        }
    };

    function initMap() {
        const initial = state.cityMetadata[state.currentCity];
        state.map = L.map('map', { center: [initial.lat, initial.lng], zoom: initial.zoom, zoomControl: false });
        L.control.zoom({ position: 'topright' }).addTo(state.map);

        // Watermark-Free, High-Detail Basemaps:
        state.baseTileLayers = {
            googleHybrid: L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
                attribution: 'Map &copy; Google / NASA Earth Observation',
                maxZoom: 20
            }),
            osm: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 19
            }),
            esriSatellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri, Earthstar Geographics, NASA',
                maxZoom: 19
            }),
            topo: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri',
                maxZoom: 19
            })
        };

        // Default to Google Hybrid Satellite (Photorealistic satellite imagery with street & river labels)
        state.baseTileLayers.googleHybrid.addTo(state.map);

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
        state.activeMarker = L.circleMarker([lat, lng], {
            radius: 8,
            fillColor: '#38bdf8',
            color: '#ffffff',
            weight: 2.5,
            fillOpacity: 1
        }).addTo(state.map);
        state.activeMarker.bindPopup(`<strong>${title}</strong><br>Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`).openPopup();
    }

    function updateCoordinateDisplay(lat, lng) {
        document.getElementById('dispLat').textContent = lat.toFixed(3);
        document.getElementById('dispLng').textContent = lng.toFixed(3);

        const kmlUrl = `/api/export/kml?lat=${lat}&lng=${lng}&city_id=${state.currentCity}`;
        const btnKML = document.getElementById('btnExportKML');
        if (btnKML) btnKML.href = kmlUrl;
        const btnSidebarKML = document.getElementById('btnExportKMLSidebar');
        if (btnSidebarKML) btnSidebarKML.href = kmlUrl;
    }

    function setupEventListeners() {
        document.getElementById('citySelect').addEventListener('change', (e) => {
            state.currentCity = e.target.value;
            loadCity(state.currentCity);
        });

        document.getElementById('btnAnalyze').addEventListener('click', () => {
            runAnalysis(state.currentCoords.lat, state.currentCoords.lng, state.currentCity);
        });

        document.getElementById('basemapSelect').addEventListener('change', (e) => {
            const chosen = e.target.value;
            Object.values(state.baseTileLayers).forEach(layer => {
                if (state.map.hasLayer(layer)) state.map.removeLayer(layer);
            });
            state.baseTileLayers[chosen].addTo(state.map);
            state.baseTileLayers[chosen].bringToBack();
            state.activeBasemap = chosen;
        });

        // Environmental Layer Radios
        const radios = document.querySelectorAll('input[name="envLayer"]');
        radios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                state.activeEnvLayer = e.target.value;
                applyLayerVisibility();
                updateLegend();
            });
        });

        // Wards Checkbox
        document.getElementById('chkWards').addEventListener('change', (e) => {
            if (state.layers.wards) {
                if (e.target.checked) state.map.addLayer(state.layers.wards);
                else state.map.removeLayer(state.layers.wards);
            }
        });

        // Opacity Slider
        const slider = document.getElementById('opacitySlider');
        slider.addEventListener('input', (e) => {
            state.opacity = parseFloat(e.target.value) / 100.0;
            document.getElementById('opacityVal').textContent = `${e.target.value}%`;
            updateLayerOpacity();
        });

        // Timeline Slider
        const timelineSlider = document.getElementById('timelineSlider');
        timelineSlider.addEventListener('input', (e) => {
            const yr = parseInt(e.target.value);
            setYear(yr);
        });

        // Timeline Clickable Ticks
        document.querySelectorAll('.timeline-ticks .tick').forEach(tick => {
            tick.addEventListener('click', () => {
                const yr = parseInt(tick.getAttribute('data-year'));
                document.getElementById('timelineSlider').value = yr;
                setYear(yr);
            });
        });

        // Play/Pause Timeline Animation
        const btnPlay = document.getElementById('btnPlayTimeline');
        btnPlay.addEventListener('click', () => {
            if (state.isPlaying) {
                stopTimelinePlay();
            } else {
                startTimelinePlay();
            }
        });
    }

    function setYear(yr) {
        state.currentYear = yr;
        document.getElementById('displayActiveYear').textContent = yr;
        document.getElementById('badgeYearDisplay').textContent = `${yr} EO`;
        fetchTemporalLayer(yr);
    }

    function startTimelinePlay() {
        state.isPlaying = true;
        const btnPlay = document.getElementById('btnPlayTimeline');
        btnPlay.innerHTML = '<i class="fa-solid fa-pause"></i> <span>Pause</span>';
        btnPlay.style.background = '#ec4899';

        state.playInterval = setInterval(() => {
            let nextYr = state.currentYear + 1;
            if (nextYr > 2026) nextYr = 2015;
            document.getElementById('timelineSlider').value = nextYr;
            setYear(nextYr);
        }, 1800);
    }

    function stopTimelinePlay() {
        state.isPlaying = false;
        clearInterval(state.playInterval);
        const btnPlay = document.getElementById('btnPlayTimeline');
        btnPlay.innerHTML = '<i class="fa-solid fa-play"></i> <span>Play</span>';
        btnPlay.style.background = '';
    }

    function updateLayerOpacity() {
        if (state.layers.vegetation) state.layers.vegetation.setStyle({ fillOpacity: state.opacity });
        if (state.layers.change) state.layers.change.setStyle({ fillOpacity: state.opacity });
    }

    function applyLayerVisibility() {
        const { smoothHeat, vegetation, change, wards } = state.layers;

        if (smoothHeat) {
            if (state.activeEnvLayer === 'heat') {
                if (!state.map.hasLayer(smoothHeat)) state.map.addLayer(smoothHeat);
            } else {
                if (state.map.hasLayer(smoothHeat)) state.map.removeLayer(smoothHeat);
            }
        }

        if (vegetation) {
            if (state.activeEnvLayer === 'vegetation') {
                if (!state.map.hasLayer(vegetation)) state.map.addLayer(vegetation);
                vegetation.setStyle({ fillOpacity: state.opacity });
            } else {
                if (state.map.hasLayer(vegetation)) state.map.removeLayer(vegetation);
            }
        }

        if (change) {
            if (state.activeEnvLayer === 'change') {
                if (!state.map.hasLayer(change)) state.map.addLayer(change);
                change.setStyle({ fillOpacity: state.opacity });
            } else {
                if (state.map.hasLayer(change)) state.map.removeLayer(change);
            }
        }

        if (wards && document.getElementById('chkWards').checked) {
            wards.bringToFront();
        }
    }

    function updateLegend() {
        const titleElem = document.getElementById('legendTitle');
        const scaleElem = document.getElementById('legendScale');

        if (state.activeEnvLayer === 'heat') {
            titleElem.textContent = 'Urban Heat Island (LST °C) • River Masked';
            scaleElem.innerHTML = `
                <div class="legend-bar heat-gradient"></div>
                <div class="legend-labels">
                    <span>&lt;28°C (Low)</span>
                    <span>34°C (Mod)</span>
                    <span>38°C (High)</span>
                    <span>&gt;40°C (Ext)</span>
                </div>
            `;
        } else if (state.activeEnvLayer === 'vegetation') {
            titleElem.textContent = 'Vegetation Density Index (NDVI)';
            scaleElem.innerHTML = `
                <div class="legend-bar veg-gradient"></div>
                <div class="legend-labels">
                    <span>Low (0-0.4)</span>
                    <span>Mod (0.4-0.8)</span>
                    <span>Dense (&gt;0.8)</span>
                </div>
            `;
        } else if (state.activeEnvLayer === 'change') {
            titleElem.textContent = 'Urban Expansion & Canopy Loss';
            scaleElem.innerHTML = `
                <div class="legend-bar change-gradient"></div>
                <div class="legend-labels">
                    <span>Expansion</span>
                    <span>Veg Loss</span>
                    <span>Stable</span>
                    <span>Greening</span>
                </div>
            `;
        } else {
            titleElem.textContent = 'Clean Satellite Basemap (No Grid)';
            scaleElem.innerHTML = '<small style="color: #94a3b8;">High-resolution true color view with municipal boundaries.</small>';
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

        loadWardsBoundary(meta.wardsFile);
        fetchTemporalLayer(state.currentYear);
        runAnalysis(meta.lat, meta.lng, cityId);
    }

    async function loadWardsBoundary(wardsFile) {
        if (state.layers.wards) {
            state.map.removeLayer(state.layers.wards);
            state.layers.wards = null;
        }

        if (!wardsFile) return;

        try {
            const wardRes = await fetch(`/api/geojson/${wardsFile}`);
            if (wardRes.ok) {
                const wardData = await wardRes.json();
                state.layers.wards = L.geoJSON(wardData, {
                    style: {
                        color: '#00f0ff',
                        weight: 2.2,
                        fillColor: '#00f0ff',
                        fillOpacity: 0.06,
                        dashArray: '5, 5'
                    },
                    onEachFeature: (f, l) => {
                        const p = f.properties;
                        const areaText = p.area_sqkm ? `${p.area_sqkm} km² (${p.area_hectares} ha)` : 'Sector';
                        l.bindTooltip(`<strong>${p.ward_name || p.zone_name}</strong><br>Area: ${areaText}<br>Risk: ${p.climate_risk_score} (${p.risk_tier})<br><small style="color:#38bdf8;">Click to inspect sector</small>`, { sticky: true });
                        
                        l.on('mouseover', () => {
                            l.setStyle({ weight: 3.5, color: '#ffffff', fillOpacity: 0.20 });
                        });
                        l.on('mouseout', () => {
                            l.setStyle({ weight: 2.2, color: '#00f0ff', fillOpacity: 0.06 });
                        });
                        l.on('click', () => {
                            const c = l.getBounds().getCenter();
                            setAnalysisPin(c.lat, c.lng, p.ward_name || p.zone_name);
                            updateZoneAreaDisplay(p);
                            runAnalysis(c.lat, c.lng, null);
                        });
                    }
                });

                if (document.getElementById('chkWards').checked) {
                    state.layers.wards.addTo(state.map);
                    state.layers.wards.bringToFront();
                }
            }
        } catch (e) {
            console.error('Error loading boundaries:', e);
        }
    }

    async function fetchTemporalLayer(year) {
        try {
            const res = await fetch(`/api/layers/temporal?year=${year}&lat=${state.currentCoords.lat}&lng=${state.currentCoords.lng}&city_id=${state.currentCity}`);
            const data = await res.json();

            // 1. Smooth Thermal Gradient via Leaflet.heat (NASA Worldview style - zero blocky squares!)
            if (state.layers.smoothHeat) {
                state.map.removeLayer(state.layers.smoothHeat);
            }

            if (typeof L.heatLayer === 'function' && data.heat_points && data.heat_points.length > 0) {
                state.layers.smoothHeat = L.heatLayer(data.heat_points, {
                    radius: 35,
                    blur: 28,
                    maxZoom: 17,
                    max: 1.0,
                    gradient: {
                        0.15: '#38bdf8', // low cool
                        0.40: '#facc15', // moderate
                        0.65: '#f97316', // high
                        0.90: '#ef4444'  // extreme
                    }
                });
            } else if (data.heat_geojson) {
                // Fallback smooth polygons with zero border
                state.layers.smoothHeat = L.geoJSON(data.heat_geojson, {
                    style: (f) => ({
                        stroke: false,
                        fillColor: f.properties.fill_color,
                        fillOpacity: state.opacity
                    })
                });
            }

            // 2. Vegetation Layer
            if (state.layers.vegetation) state.map.removeLayer(state.layers.vegetation);
            if (data.veg_geojson) {
                state.layers.vegetation = L.geoJSON(data.veg_geojson, {
                    style: (f) => ({
                        stroke: false,
                        fillColor: f.properties.fill_color,
                        fillOpacity: state.opacity
                    })
                });
            }

            // 3. Update telemetry for this year
            renderMetrics(data);
            renderRiskScore(data.resilience_and_risk);
            if (data.map_area_intelligence) {
                renderAreaIntelligence(data.map_area_intelligence);
            }

            applyLayerVisibility();
            updateLegend();

        } catch (err) {
            console.error('Temporal layer error:', err);
        }
    }

    function updateZoneAreaDisplay(p) {
        if (p.area_sqkm) {
            document.getElementById('dispTotalArea').innerHTML = `${p.area_sqkm} km² <small>(${p.area_hectares} ha)</small>`;
            const builtPct = Math.round(55 + p.mean_ndbi * 60);
            const greenPct = Math.round(p.mean_ndvi * 75);
            const waterPct = Math.max(2, 100 - builtPct - greenPct);
            
            document.getElementById('dispBuiltUpArea').textContent = `${(p.area_sqkm * builtPct / 100).toFixed(2)} km² (${builtPct}%)`;
            document.getElementById('barBuiltUp').style.width = `${builtPct}%`;
            
            document.getElementById('dispGreenArea').textContent = `${(p.area_sqkm * greenPct / 100).toFixed(2)} km² (${greenPct}%)`;
            document.getElementById('barGreen').style.width = `${greenPct}%`;
            
            document.getElementById('dispWaterArea').textContent = `${(p.area_sqkm * waterPct / 100).toFixed(2)} km² (${waterPct}%)`;
            document.getElementById('barWater').style.width = `${waterPct}%`;
            
            if (p.landmarks) {
                document.getElementById('dispZoneLandmarks').textContent = p.landmarks;
            }
        }
    }

    async function runAnalysis(lat, lng, cityId) {
        try {
            const resp = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat, lng, city_id: cityId, year_start: 2015, year_end: state.currentYear })
            });
            const data = await resp.json();
            renderMetrics(data);
            renderRiskScore(data.resilience_and_risk);
            renderTrendChart(data.temporal_trends);
            renderRecommendations(data.recommendations);
            
            if (data.map_area_intelligence) {
                renderAreaIntelligence(data.map_area_intelligence);
            }

            // Also load urban change layer
            const changeRes = await fetch(`/api/layers/urban-change?lat=${lat}&lng=${lng}&grid_km=10`);
            const changeData = await changeRes.json();
            if (state.layers.change) state.map.removeLayer(state.layers.change);
            state.layers.change = L.geoJSON(changeData.geojson, {
                style: (f) => ({
                    stroke: false,
                    fillColor: f.properties.fill_color,
                    fillOpacity: state.opacity
                })
            });
            applyLayerVisibility();

        } catch (err) {
            console.error('Analysis error:', err);
        }
    }

    function renderAreaIntelligence(areaData) {
        document.getElementById('dispTotalArea').innerHTML = `${areaData.total_area_sqkm} km² <small>(${areaData.total_area_hectares} ha)</small>`;
        document.getElementById('dispBuiltUpArea').textContent = `${areaData.built_up_area_sqkm} km² (${areaData.built_up_pct}%)`;
        document.getElementById('barBuiltUp').style.width = `${areaData.built_up_pct}%`;
        
        document.getElementById('dispGreenArea').textContent = `${areaData.green_canopy_sqkm} km² (${areaData.green_canopy_pct}%)`;
        document.getElementById('barGreen').style.width = `${areaData.green_canopy_pct}%`;
        
        document.getElementById('dispWaterArea').textContent = `${areaData.water_body_sqkm} km² (${areaData.water_body_pct}%)`;
        document.getElementById('barWater').style.width = `${areaData.water_body_pct}%`;
    }

    function renderMetrics(data) {
        const thermal = data.thermal_intelligence;
        const veg = data.vegetation_intelligence;
        const change = data.change_detection ? data.change_detection.metrics : { built_up_change_pct: 32.5, vegetation_change_pct: -16.4 };

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
        riskData.reasons.forEach(r => {
            const li = document.createElement('li');
            li.textContent = r;
            listElem.appendChild(li);
        });
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
                responsive: true,
                maintainAspectRatio: false,
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
