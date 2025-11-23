const API_URL = 'http://localhost:8000';

let selectedPerovskite = null;
let selectedQD = null;
let bandChart = null;
let screeningResults = []; // Store the fetched results globally
let currentSort = { column: 'strain', direction: 'asc' };

async function searchPerovskite() {
    const query = document.getElementById('perovskite-search').value;
    const resultsDiv = document.getElementById('perovskite-results');
    resultsDiv.innerHTML = 'Loading...';

    try {
        const response = await fetch(`${API_URL}/search?formula=${query}`);
        const data = await response.json();
        displayResults(data, resultsDiv, 'perovskite');
    } catch (error) {
        resultsDiv.innerHTML = 'Error fetching results.';
        console.error(error);
    }
}

async function searchQD() {
    const query = document.getElementById('qd-search').value;
    const resultsDiv = document.getElementById('qd-results');
    resultsDiv.innerHTML = 'Loading...';

    try {
        const response = await fetch(`${API_URL}/search?formula=${query}`);
        const data = await response.json();
        displayResults(data, resultsDiv, 'qd');
    } catch (error) {
        resultsDiv.innerHTML = 'Error fetching results.';
        console.error(error);
    }
}

function displayResults(data, container, type) {
    container.innerHTML = '';
    if (data.length === 0) {
        container.innerHTML = 'No results found.';
        return;
    }

    data.forEach(item => {
        const div = document.createElement('div');
        div.className = 'result-item';
        div.innerHTML = `<strong>${item.formula}</strong> (ID: ${item.material_id}) - Bandgap: ${item.band_gap.toFixed(2)} eV`;
        div.onclick = () => selectMaterial(item, type);
        container.appendChild(div);
    });
}

function selectMaterial(item, type) {
    if (type === 'perovskite') {
        selectedPerovskite = item;
        const el = document.getElementById('selected-perovskite');
        el.style.display = 'block';
        el.innerHTML = `Selected: <strong>${item.formula}</strong><br>Bandgap: ${item.band_gap.toFixed(2)} eV`;
    } else {
        selectedQD = item;
        const el = document.getElementById('selected-qd');
        el.style.display = 'block';
        el.innerHTML = `Selected: <strong>${item.formula}</strong><br>Bandgap: ${item.band_gap.toFixed(2)} eV`;
    }

    checkAnalyzeButton();
}

function checkAnalyzeButton() {
    const btn = document.getElementById('analyze-btn');
    btn.disabled = !(selectedPerovskite && selectedQD);
}

async function analyzeHeterojunction() {
    if (!selectedPerovskite || !selectedQD) return;

    const resultsSection = document.getElementById('analysis-results');
    resultsSection.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                perovskite_formula: selectedPerovskite.formula,
                qd_formula: selectedQD.formula
            })
        });

        const data = await response.json();

        document.getElementById('strain-value').textContent = `${data.lattice_mismatch_percent}%`;
        document.getElementById('strain-note').textContent = data.lattice_mismatch_percent < 5 ? "Good Match (<5%)" : "High Strain (>5%)";

        document.getElementById('alignment-value').textContent = Math.abs(data.band_gap_1 - data.band_gap_2).toFixed(2) + " eV";
        document.getElementById('alignment-note').textContent = data.band_alignment_note;

        renderBandDiagram(data);

    } catch (error) {
        console.error(error);
        alert('Analysis failed.');
    }
}

function renderBandDiagram(data) {
    const ctx = document.getElementById('bandDiagram').getContext('2d');

    if (bandChart) bandChart.destroy();

    // Simple visualization: Bar chart showing VBM and CBM relative to a common reference
    // Since we don't have absolute vacuum levels, we'll align the VBM of material 1 to 0 for visualization purposes
    // This is purely illustrative of the GAPS, not the ALIGNMENT (unless we had electron affinity)
    // To make it useful, we'll just show the band gaps side by side for now.

    bandChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [data.material1, data.material2],
            datasets: [
                {
                    label: 'Conduction Band Min (Relative)',
                    data: [data.band_gap_1, data.band_gap_2], // Height of the bar
                    backgroundColor: ['rgba(98, 0, 234, 0.5)', 'rgba(3, 218, 198, 0.5)'],
                    borderColor: ['rgba(98, 0, 234, 1)', 'rgba(3, 218, 198, 1)'],
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Energy (eV)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Band Gap Comparison'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Band Gap: ${context.raw} eV`;
                        }
                    }
                }
            }
        }
    });
}

// Screening Logic

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => {
        if (b.textContent.toLowerCase().includes(tab === 'single' ? 'single' : 'screening')) {
            b.classList.add('active');
        }
    });

    if (tab === 'single') {
        document.getElementById('single-view').classList.remove('hidden');
        document.getElementById('screen-view').classList.add('hidden');
    } else {
        document.getElementById('single-view').classList.add('hidden');
        document.getElementById('screen-view').classList.remove('hidden');
    }
}

async function runScreening() {
    const loading = document.getElementById('screening-loading');
    const resultsDiv = document.getElementById('screening-results');

    loading.classList.remove('hidden');
    resultsDiv.innerHTML = '';

    const payload = {
        max_strain: parseFloat(document.getElementById('max-strain').value),
        min_perovskite_bandgap: parseFloat(document.getElementById('min-p-bg').value),
        max_perovskite_bandgap: parseFloat(document.getElementById('max-p-bg').value),
        min_qd_bandgap: parseFloat(document.getElementById('min-q-bg').value),
        max_qd_bandgap: parseFloat(document.getElementById('max-q-bg').value)
    };

    try {
        const response = await fetch(`${API_URL}/screen`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        screeningResults = data; // Store results
        renderScreeningResults(); // Render with current sort
    } catch (error) {
        console.error(error);
        resultsDiv.innerHTML = '<p style="color: var(--error)">Screening failed. Please try again.</p>';
    } finally {
        loading.classList.add('hidden');
    }
}

function sortResults(column) {
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc'; // Default to ascending for new column
    }
    renderScreeningResults();
}

function renderScreeningResults() {
    const resultsDiv = document.getElementById('screening-results');
    if (!screeningResults || screeningResults.length === 0) {
        resultsDiv.innerHTML = '<p>No compatible pairs found. Try adjusting filters.</p>';
        return;
    }

    // Sort data
    const sortedData = [...screeningResults].sort((a, b) => {
        let valA = a[currentSort.column];
        let valB = b[currentSort.column];

        // Handle special cases if needed (e.g. strings vs numbers)
        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();

        if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
        if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });

    let html = `
        <table class="screening-table">
            <thead>
                <tr>
                    <th onclick="sortResults('perovskite')" style="cursor: pointer;">Perovskite ${getSortIcon('perovskite')}</th>
                    <th onclick="sortResults('qd')" style="cursor: pointer;">Quantum Dot ${getSortIcon('qd')}</th>
                    <th onclick="sortResults('strain')" style="cursor: pointer;">Lattice Mismatch ${getSortIcon('strain')}</th>
                    <th onclick="sortResults('perovskite_bg')" style="cursor: pointer;">P-Bandgap ${getSortIcon('perovskite_bg')}</th>
                    <th onclick="sortResults('qd_bg')" style="cursor: pointer;">QD-Bandgap ${getSortIcon('qd_bg')}</th>
                </tr>
            </thead>
            <tbody>
    `;

    sortedData.forEach(row => {
        const strainClass = row.strain < 2 ? 'tag-good' : 'tag-warn';
        html += `
            <tr onclick="window.open('/static/details.html?pid=${row.perovskite_id}&qid=${row.qd_id}', '_blank')" style="cursor: pointer;">
                <td>${row.perovskite}</td>
                <td>${row.qd}</td>
                <td><span class="tag ${strainClass}">${row.strain.toFixed(2)}%</span></td>
                <td>${row.perovskite_bg.toFixed(2)} eV</td>
                <td>${row.qd_bg.toFixed(2)} eV</td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    resultsDiv.innerHTML = html;
}

function getSortIcon(column) {
    if (currentSort.column !== column) return '↕';
    return currentSort.direction === 'asc' ? '↑' : '↓';
}
