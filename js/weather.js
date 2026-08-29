/* Local HVAC Outlook — visitor-local weather + demand read
   Uses Open-Meteo (free, no API key, global, CORS-enabled).
   Data source: https://open-meteo.com/en/docs */
(function () {
  "use strict";

  const GEOCODE = "https://geocoding-api.open-meteo.com/v1/search";
  const FORECAST = "https://api.open-meteo.com/v1/forecast";
  const BASE_F = 65; // degree-day base (°F)

  const root = document.getElementById("outlook");
  if (!root) return;

  const form = root.querySelector("#outlook-form");
  const input = root.querySelector("#outlook-city");
  const geoBtn = root.querySelector("#outlook-geo");
  const status = root.querySelector("#outlook-status");
  const result = root.querySelector("#outlook-result");

  const c2f = (c) => (c * 9) / 5 + 32;
  const fmtF = (f) => Math.round(f) + "°F";
  const escHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));

  function dayName(iso, tz) {
    try {
      const d = new Date(iso + "T12:00:00");
      return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", timeZone: tz });
    } catch (e) {
      return iso;
    }
  }

  function statusMsg(msg, isErr) {
    status.textContent = msg;
    status.style.color = isErr ? "var(--color-danger, #c0392b)" : "var(--color-text-muted)";
  }

  async function loadByCoords(lat, lon, label) {
    statusMsg("Fetching forecast…");
    const url = FORECAST +
      "?latitude=" + lat + "&longitude=" + lon +
      "&daily=temperature_2m_max,temperature_2m_min,relative_humidity_2m_max,precipitation_sum" +
      "&timezone=auto&forecast_days=7";
    let data;
    try {
      const r = await fetch(url);
      if (!r.ok) throw new Error("HTTP " + r.status);
      data = await r.json();
    } catch (e) {
      statusMsg("Could not reach the forecast service. Try again.", true);
      return;
    }
    render(label, data);
  }

  function render(label, data) {
    const d = data.daily;
    const tz = data.timezone;
    const rows = d.time.map((iso, i) => ({
      iso, day: dayName(iso, tz),
      hi: c2f(d.temperature_2m_max[i]),
      lo: c2f(d.temperature_2m_min[i]),
      hum: d.relative_humidity_2m_max[i],
      precip: d.precipitation_sum[i],
    }));

    let cdd = 0, hdd = 0, maxHi = -999, minLo = 999, wetDays = 0, humSum = 0, hotDays = 0, coldDays = 0;
    rows.forEach((r) => {
      const avg = (r.hi + r.lo) / 2;
      if (avg > BASE_F) cdd += avg - BASE_F; else hdd += BASE_F - avg;
      if (r.hi > maxHi) maxHi = r.hi;
      if (r.lo < minLo) minLo = r.lo;
      if (r.hum != null) humSum += r.hum;
      if (r.precip >= 5) wetDays++;
      if (r.hi >= 90) hotDays++;
      if (r.lo <= 32) coldDays++;
    });
    const avgHum = humSum / rows.length;

    const flags = [];
    if (hotDays >= 2) flags.push({ tone: "danger", text: "Heat wave this week — expect peak cooling load. Confirm AC capacity, filter condition, and refrigerant charge before the hottest day." });
    else if (hotDays === 1) flags.push({ tone: "warn", text: "One very hot day — cooling demand spikes. A good time for a quick filter check." });
    if (coldDays >= 2) flags.push({ tone: "danger", text: "Cold snap — peak heating load. Verify furnace/heat pump operation and combustion safety." });
    if (avgHum >= 70) flags.push({ tone: "warn", text: "High humidity most of the week — dehumidification matters; watch indoor moisture and IAQ." });
    else if (avgHum < 35) flags.push({ tone: "info", text: "Dry air — low humidity can irritate airways; consider humidification if indoor RH drops below 30%." });
    if (wetDays >= 2) flags.push({ tone: "info", text: "Wet stretch — check drainage around equipment and watch for indoor humidity spikes." });
    if (!flags.length) flags.push({ tone: "ok", text: "Mild week ahead — low HVAC demand. A good window for seasonal maintenance and upgrades." });

    const demandLabel = (cdd > hdd) ? "Cooling-dominant week" : (hdd > 0 ? "Heating-dominant week" : "Low-demand week");

    const rowsHtml = rows.map((r) => {
      const tempBar = r.hi >= 90 ? "warm" : r.lo <= 32 ? "cool" : "mild";
      return '<tr><td>' + r.day + '</td>' +
        '<td>' + fmtF(r.hi) + ' / ' + fmtF(r.lo) + '</td>' +
        '<td>' + (r.hum != null ? Math.round(r.hum) + "%" : "—") + '</td>' +
        '<td>' + (r.precip != null ? r.precip.toFixed(1) + " mm" : "—") + '</td>' +
        '<td><span class="demand-dot demand-' + tempBar + '"></span>' +
        (r.hi >= 90 ? "High cooling" : r.lo <= 32 ? "High heating" : "Mild") + '</td></tr>';
    }).join("");

    const flagsHtml = flags.map((f) =>
      '<div class="callout callout--' + f.tone + '">' + f.text + "</div>"
    ).join("");

    result.innerHTML =
      '<div class="outlook-head"><div><h3 class="outlook-loc">' + escHtml(label) + '</h3>' +
      '<p class="outlook-sub">' + demandLabel + ' · Cooling degree-days: ' + Math.round(cdd) +
      ' · Heating degree-days: ' + Math.round(hdd) + '</p></div>' +
      '<div class="outlook-extreme"><span class="big">' + fmtF(maxHi) + '</span><span>week high</span>' +
      '<span class="big">' + fmtF(minLo) + '</span><span>week low</span></div></div>' +
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Day</th><th>Hi / Lo</th><th>RH</th><th>Precip</th><th>Demand</th></tr></thead><tbody>' + rowsHtml + '</tbody></table></div>' +
      '<div class="outlook-flags">' + flagsHtml + '</div>' +
      '<p class="outlook-source">Forecast: <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a>. Degree-day base 65°F. Informational — not a substitute for a site assessment by a licensed HVAC professional.</p>';

    result.style.display = "block";
    statusMsg("");
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = (input.value || "").trim();
    if (q.length < 2) { statusMsg("Enter a city or postal code.", true); return; }
    statusMsg("Looking up location…");
    let geo;
    try {
      const r = await fetch(GEOCODE + "?name=" + encodeURIComponent(q) + "&count=1&language=en&format=json");
      if (!r.ok) throw new Error();
      const j = await r.json();
      geo = j.results && j.results[0];
    } catch (err) { statusMsg("Geocoding failed. Try again.", true); return; }
    if (!geo) { statusMsg("Location not found. Try a nearby city.", true); return; }
    const label = [geo.name, geo.admin1, geo.country_code].filter(Boolean).join(", ");
    await loadByCoords(geo.latitude, geo.longitude, label);
  });

  geoBtn.addEventListener("click", () => {
    if (!navigator.geolocation) { statusMsg("Geolocation isn't available — search a city instead.", true); return; }
    statusMsg("Waiting for location permission…");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude.toFixed(3);
        const lon = pos.coords.longitude.toFixed(3);
        loadByCoords(lat, lon, "Your location (" + lat + ", " + lon + ")");
      },
      () => { statusMsg("Location permission denied — search a city instead.", true); },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 600000 }
    );
  });

  // Optionally auto-load with a default so the section isn't empty on first view
  loadByCoords(40.74, -74.17, "Newark, NJ, US");
})();
