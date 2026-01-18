<script>
	import { onMount, tick } from 'svelte';
	import { flip } from 'svelte/animate';
	import { fade, fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	export let data;

	$: ({ mapData, rankStats, timeline, surnames } = data);

	// --- Process Data for Charts ---
	let maxDeaths = 0;
	$: if (timeline && timeline.length) {
		maxDeaths = Math.max(...timeline.map((d) => d.total_deaths));
	}

	// --- Annotations ---
	const notableDates = [
		{ date: '1915-10-13', label: '13 Oct 1915' },
		{ date: '1916-07-01', label: '1 Jul 1916' },
		{ date: '1918-03-20', label: '20 Mar 1918' }
	];

	let annotations = [];
	$: if (timeline && timeline.length) {
		annotations = notableDates
			.map((d) => {
				const idx = timeline.findIndex((t) => t.iso_date === d.date);
				return idx !== -1 ? { x: idx, label: d.label } : null;
			})
			.filter(Boolean);
	}

	// --- Rank Sorting ---
	$: if (rankStats && rankStats.length > 0) console.log('Rank Stats Data:', rankStats[0]);

	$: sortedRanks = [...rankStats]
		.map((r) => ({ ...r, total_deaths: Number(r.count || r.total_deaths) }))
		.sort((a, b) => b.total_deaths - a.total_deaths)
		.slice(0, 20);

	$: maxRankCount = sortedRanks.length > 0 ? sortedRanks[0].total_deaths : 1;

	$: maxSurnameCount =
		displaySurnames.length > 0 ? Math.max(...displaySurnames.map((s) => s.total_count)) : 1;

	// --- Surname Filtering ---
	let surnameFilter = 'total_count'; // total_count, north_staffs_count, south_staffs_count
	$: displaySurnames = [...surnames]
		.sort((a, b) => b[surnameFilter] - a[surnameFilter])
		.slice(0, 20);

	// --- Timeline Interaction ---
	let hoveredDay = null;
	let mouseX = 0;
	let mouseY = 0;

	function handleMouseMove(e) {
		const rect = e.currentTarget.getBoundingClientRect();
		mouseX = e.clientX - rect.left;
		mouseY = e.clientY - rect.top;
	}

	// --- Map Logic ---
	let mapContainer;
	onMount(async () => {
		if (typeof window !== 'undefined') {
			const L = await import('leaflet');

			// Initialize map - Center roughly between Manchester (West/Left) and Frontline (East/Right)
			const map = L.map(mapContainer).setView([51.8, 0.4], 7);

			L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>, Data: Commonwealth War Grave Commission',
				maxZoom: 20
			}).addTo(map);

			// Add circles
			console.log('Map Data Length:', mapData.length);

			mapData.forEach((site, i) => {
				if (i < 3) console.log('Processing site:', site); // Debug first few

				// Check for coordinates array [lat, lng]
				if (site.coordinates && site.coordinates.length === 2) {
					// Extract lat/lng from array
					// PostGIS often returns [long, lat] or [lat, long]. Debug showed 40.X, 26.X for Gallipoli.
					// Gallipoli is 40N, 26E.
					// If logs showed [40.4, 26.3], then coordinates[0] is LAT, coordinates[1] is LNG.
					const latitude = Number(site.coordinates[0]);
					const longitude = Number(site.coordinates[1]);

					// Fallback for num_commemorated if missing
					// If missing, count the fallen_list
					const count = site.num_commemorated || (site.fallen_list ? site.fallen_list.length : 1);

					// Basic validation
					if (!isNaN(latitude) && !isNaN(longitude)) {
						const radius = Math.sqrt(count) * 500;

						const circle = L.circle([latitude, longitude], {
							color: '#b22222',
							fillColor: '#b22222',
							fillOpacity: 0.6,
							radius: radius,
							weight: 1
						}).addTo(map);

						circle.bindPopup(`
							<div class="map-popup">
								<h3>${site.cemetery_name}</h3>
								<div class="stat">${count} fatalities</div>
								<div class="divider"></div>
								<div class="bio-list">
									${
										site.fallen_list
											? site.fallen_list
													.filter((f) => f.bio && f.bio !== 'null')
													.map((f) => `<p>${f.bio}</p>`)
													.join('')
											: 'No details available'
									}
								</div>
							</div>
						`);
					}
				}
			});

			// Fix map rendering issues by invalidating size after mount
			setTimeout(() => {
				map.invalidateSize();
			}, 150);
		}
	});

	// --- Formatter ---
	const formatDate = (iso) => {
		return new Date(iso).toLocaleDateString('en-GB', {
			day: 'numeric',
			month: 'short',
			year: 'numeric'
		});
	};
</script>

<svelte:head>
	<link
		rel="stylesheet"
		href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
		integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
		crossorigin=""
	/>
</svelte:head>

<main class="dashboard">
	<div class="intro-header">
		<h1>Staffordshire War Dead</h1>
		<p class="intro-text">
			I created a simple visualisation to remember the 7,000 or so men from the North Staffordshire
			regiment who were killed during the first world war. This project began in 2012 and was
			extended to cover the South Staffordshire Regiment. I've used the same data from the
			Commonwealth War Graves Commission using Python and Svelte. Users can explore the map and
			click on those commemorated. I'm looking to develop the platform further.
		</p>
	</div>

	<!-- Map -->
	<section class="card map-section">
		<div class="map-header-row">
			<h3>Memorial Map</h3>
			<p class="map-hint">
				<span class="hint-icon">👆</span> Zoom in and click circles to see details
			</p>
		</div>
		<div bind:this={mapContainer} id="map-container"></div>
	</section>

	<!-- Timeline Section -->
	<section class="card timeline-section">
		<header class="section-header">
			<div>
				<h2>Daily Death Timeline</h2>
				<p class="subtitle">1914 &mdash; 1918</p>
			</div>

			<div class="header-info">
				{#if hoveredDay}
					<div class="static-tooltip" transition:fade>
						<span class="st-date">{formatDate(hoveredDay.iso_date)}</span>
						<span class="st-total">Total: <strong>{hoveredDay.total_deaths}</strong></span>
						<span class="st-north">North: <strong>{hoveredDay.north_staffs}</strong></span>
						<span class="st-south">South: <strong>{hoveredDay.south_staffs}</strong></span>
					</div>
				{/if}
			</div>

			<div class="legend">
				<div class="legend-item"><span class="swatch north"></span> North Staffs</div>
				<div class="legend-item"><span class="swatch south"></span> South Staffs</div>
			</div>
		</header>

		<div class="viz-wrapper">
			<div class="y-axis-label">Number of deaths (daily)</div>
			<div
				class="timeline-viz"
				role="application"
				aria-label="Daily death timeline"
				on:mousemove={handleMouseMove}
				on:mouseleave={() => (hoveredDay = null)}
			>
				<svg viewBox="0 0 {Math.max(timeline.length, 100)} 350" preserveAspectRatio="none">
					<!-- Annotation Lines -->
					{#each annotations as ann}
						<line
							x1={ann.x}
							y1="0"
							x2={ann.x}
							y2="350"
							stroke="#333"
							stroke-width="1"
							stroke-dasharray="5,3"
							opacity="0.6"
						/>
						<text
							x={ann.x + 4}
							y="15"
							font-size="10"
							fill="#333"
							font-weight="bold"
							style="text-shadow: 0 0 2px white;">{ann.label}</text
						>
					{/each}

					{#each timeline as day, i}
						{@const hSouth = (day.south_staffs / maxDeaths) * 350}
						{@const hNorth = (day.north_staffs / maxDeaths) * 350}

						<g
							class="bar-group"
							on:mouseenter={() => (hoveredDay = day)}
							role="graphics-symbol"
							aria-label="{day.iso_date}: {day.total_deaths} deaths"
						>
							<rect
								x={i}
								y={350 - hSouth}
								width="3"
								height={Math.max(0, hSouth)}
								fill="#cc6600"
								shape-rendering="crispEdges"
							/>
							<rect
								x={i}
								y={350 - hSouth - hNorth}
								width="3"
								height={Math.max(0, hNorth)}
								fill="#004488"
								shape-rendering="crispEdges"
							/>
						</g>
					{/each}
				</svg>

				<!-- Hover Tooltip -->
				{#if hoveredDay}
					<div
						class="floating-tooltip"
						style="left: {Math.min(mouseX + 20, 1200)}px; top: {mouseY}px"
					>
						<div class="tooltip-date">{formatDate(hoveredDay.iso_date)}</div>
						<div class="tooltip-row total">
							<span>Total</span>
							<strong>{hoveredDay.total_deaths}</strong>
						</div>
						<div class="tooltip-row north">
							<span>North Staffs</span>
							<strong>{hoveredDay.north_staffs}</strong>
						</div>
						<div class="tooltip-row south">
							<span>South Staffs</span>
							<strong>{hoveredDay.south_staffs}</strong>
						</div>
					</div>
				{/if}

				<div class="x-axis">
					<span>1914</span>
					<span>1915</span>
					<span>1916</span>
					<span class="neutral-label">Date</span>
					<span>1917</span>
					<span>1918</span>
				</div>
			</div>
		</div>
	</section>

	<div class="grid-2">
		<!-- Rank Stats -->
		<section class="card">
			<h3>Deaths by Rank</h3>
			<div class="chart-container">
				{#each sortedRanks as r}
					<div class="rank-row">
						<span class="rank-label">{r.rank}</span>
						<div class="bar-area">
							<div class="bar-fill" style="width: {(r.total_deaths / maxRankCount) * 100}%"></div>
							<span class="bar-value" style="left: {(r.total_deaths / maxRankCount) * 100}%">
								{r.total_deaths.toLocaleString()}
							</span>
						</div>
					</div>
				{/each}
			</div>
		</section>

		<!-- Surnames -->
		<section class="card">
			<div class="card-header-flex">
				<div class="rh-col">
					<h3>Top 20 Surnames</h3>
					<div class="legend mini">
						<div class="legend-item"><span class="swatch north"></span> North</div>
						<div class="legend-item"><span class="swatch south"></span> South</div>
					</div>
				</div>
				<div class="toggle-group">
					<button
						class:active={surnameFilter === 'total_count'}
						on:click={() => (surnameFilter = 'total_count')}>All</button
					>
					<button
						class:active={surnameFilter === 'north_staffs_count'}
						on:click={() => (surnameFilter = 'north_staffs_count')}
						class="btn-north">North</button
					>
					<button
						class:active={surnameFilter === 'south_staffs_count'}
						on:click={() => (surnameFilter = 'south_staffs_count')}
						class="btn-south">South</button
					>
				</div>
			</div>

			<div class="surname-list">
				{#each displaySurnames as s (s.surname)}
					<div class="surname-row" animate:flip={{ duration: 450, easing: quintOut }}>
						<div class="name-col">{s.surname}</div>
						<div class="viz-col">
							<!-- Stacked Bar Container -->
							<div class="viz-track">
								{#if surnameFilter === 'north_staffs_count'}
									<!-- North First -->
									{#if s.north_staffs_count > 0}
										<div
											class="viz-segment n"
											style="width: {(s.north_staffs_count / maxSurnameCount) * 100}%"
										>
											<span class="seg-label">{s.north_staffs_count}</span>
										</div>
									{/if}
									{#if s.south_staffs_count > 0}
										<div
											class="viz-segment s"
											style="width: {(s.south_staffs_count / maxSurnameCount) * 100}%"
										>
											<span class="seg-label">{s.south_staffs_count}</span>
										</div>
									{/if}
								{:else}
									<!-- South First (Default) -->
									{#if s.south_staffs_count > 0}
										<div
											class="viz-segment s"
											style="width: {(s.south_staffs_count / maxSurnameCount) * 100}%"
										>
											<span class="seg-label">{s.south_staffs_count}</span>
										</div>
									{/if}
									{#if s.north_staffs_count > 0}
										<div
											class="viz-segment n"
											style="width: {(s.north_staffs_count / maxSurnameCount) * 100}%"
										>
											<span class="seg-label">{s.north_staffs_count}</span>
										</div>
									{/if}
								{/if}
							</div>
						</div>
						<div class="count-col">{s.total_count}</div>
					</div>
				{/each}
			</div>
		</section>
	</div>
</main>

<style>
	:global(body) {
		background-color: #f4f4f9;
		font-family:
			'Inter',
			-apple-system,
			BlinkMacSystemFont,
			'Segoe UI',
			Roboto,
			Oxygen,
			Ubuntu,
			Cantarell,
			'Open Sans',
			'Helvetica Neue',
			sans-serif;
		margin: 0;
	}

	.dashboard {
		max-width: 1400px;
		margin: 0 auto;
		padding: 24px;
		display: grid;
		gap: 24px;
	}

	.intro-header {
		margin-bottom: 8px;
	}
	h1 {
		font-size: 2rem;
		font-weight: 800;
		color: #1a1a1a;
		margin: 0 0 16px;
	}
	.intro-text {
		max-width: 800px;
		line-height: 1.6;
		color: #444;
		font-size: 1.1rem;
		margin: 0;
	}

	.map-header-row {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		margin-bottom: 1rem;
	}
	.map-header-row h3 {
		margin-bottom: 0;
	}
	.map-hint {
		font-size: 0.85rem;
		color: #666;
		background: #f5f5f5;
		padding: 4px 12px;
		border-radius: 20px;
		display: flex;
		align-items: center;
		gap: 6px;
		margin: 0;
	}
	.hint-icon {
		font-size: 1rem;
	}

	.card {
		background: white;
		border-radius: 12px;
		box-shadow:
			0 4px 6px -1px rgba(0, 0, 0, 0.1),
			0 2px 4px -1px rgba(0, 0, 0, 0.06);
		padding: 24px;
		overflow: hidden;
	}

	h2,
	h3 {
		margin: 0;
		color: #1a1a1a;
	}

	h2 {
		font-size: 1.5rem;
		font-weight: 700;
	}
	h3 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 1rem;
	}
	.subtitle {
		margin: 4px 0 0;
		color: #666;
		font-size: 0.9rem;
	}

	/* Timeline */
	.timeline-section {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
	}
	.legend {
		display: flex;
		gap: 16px;
	}
	.legend-item {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 0.85rem;
		font-weight: 500;
	}
	.swatch {
		width: 12px;
		height: 12px;
		border-radius: 2px;
	}
	.swatch.north {
		background: #004488;
	}
	.swatch.south {
		background: #cc6600;
	}

	.timeline-viz {
		position: relative;
		width: 100%;
		height: 380px;
		cursor: crosshair;
	}
	svg {
		width: 100%;
		height: 350px;
		background: #fafafa;
		border-bottom: 1px solid #ddd;
	}
	.bar-group rect {
		transition: opacity 0.1s;
	}
	.bar-group:hover rect {
		opacity: 0.8;
	}

	.x-axis {
		display: flex;
		justify-content: space-between;
		padding-top: 8px;
		font-size: 0.8rem;
		color: #666;
		font-weight: 600;
	}
	.center-label {
		color: #b22222;
		font-weight: 700;
	}

	.floating-tooltip {
		position: absolute;
		background: rgba(255, 255, 255, 0.95);
		border: 1px solid #eee;
		padding: 12px;
		border-radius: 8px;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
		pointer-events: none;
		z-index: 100;
		min-width: 160px;
		backdrop-filter: blur(4px);
	}
	.tooltip-date {
		font-size: 0.85rem;
		color: #444;
		margin-bottom: 8px;
		border-bottom: 1px solid #eee;
		padding-bottom: 4px;
	}
	.tooltip-row {
		display: flex;
		justify-content: space-between;
		font-size: 0.8rem;
		margin-bottom: 4px;
	}
	.tooltip-row.total {
		color: #000;
		font-weight: 600;
	}
	.tooltip-row.north {
		color: #004488;
	}
	.tooltip-row.south {
		color: #cc6600;
	}

	/* Grid Layout */
	.grid-2 {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px;
	}

	/* Header Info & Static Tooltip */
	.header-info {
		flex: 1;
		display: flex;
		justify-content: center;
		height: 48px; /* Fixed height to prevent jumping */
		align-items: center;
	}
	.static-tooltip {
		display: flex;
		gap: 16px;
		background: #fafafa;
		padding: 6px 16px;
		border-radius: 20px;
		border: 1px solid #eee;
		font-size: 0.9rem;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
	}
	.st-date {
		font-weight: 600;
		color: #444;
		border-right: 1px solid #ddd;
		padding-right: 12px;
		margin-right: -4px;
	}
	.st-total strong {
		color: #000;
	}
	.st-north strong {
		color: #004488;
	}
	.st-south strong {
		color: #cc6600;
	}

	/* Viz Wrapper & Y-Axis */
	.viz-wrapper {
		display: flex;
		gap: 12px;
		align-items: flex-end; /* Align chart bottom with axis label */
	}
	.y-axis-label {
		writing-mode: vertical-rl;
		transform: rotate(180deg);
		font-size: 0.75rem;
		font-weight: 600;
		color: #666;
		text-align: center;
		height: 350px;
		margin-bottom: 30px; /* Offset for X-axis height */
	}
	.neutral-label {
		color: #666;
		font-weight: 600;
	}
	@media (max-width: 768px) {
		.grid-2 {
			grid-template-columns: 1fr;
		}
	}

	/* Rank Chart */
	.rank-row {
		display: flex;
		align-items: center;
		margin-bottom: 8px;
	}
	.rank-label {
		width: 140px;
		text-align: right;
		font-size: 0.85rem;
		padding-right: 12px;
		color: #444;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.bar-area {
		flex: 1;
		background: #f0f0f0;
		height: 24px;
		border-radius: 4px;
		position: relative; /* Helper for absolute label */
		margin-right: 48px; /* Space for external label */
	}
	.bar-fill {
		height: 100%;
		background: linear-gradient(90deg, #444, #666);
		border-radius: 4px; /* Fix border radius */
	}
	.bar-value {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		margin-left: 8px;
		font-size: 0.75rem;
		font-weight: 600;
		color: #333;
		white-space: nowrap;
	}

	/* Surnames */
	.card-header-flex {
		display: flex;
		justify-content: space-between;
		align-items: flex-end; /* Align bottom to match legend */
		margin-bottom: 16px;
	}
	.rh-col {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.legend.mini {
		font-size: 0.75rem;
		margin-top: 2px;
	}

	.toggle-group {
		display: flex;
		gap: 4px;
		background: #f0f0f0;
		padding: 4px;
		border-radius: 8px;
	}
	.toggle-group button {
		border: none;
		background: none;
		padding: 4px 12px;
		font-size: 0.75rem;
		cursor: pointer;
		border-radius: 6px;
		font-weight: 600;
		color: #666;
		transition: all 0.2s;
	}
	.toggle-group button.active {
		background: white;
		color: #000;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}
	.toggle-group button.btn-north.active {
		color: #004488;
	}
	.toggle-group button.btn-south.active {
		color: #cc6600;
	}

	.surname-list {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.surname-row {
		display: flex;
		align-items: center;
		padding: 6px 0;
		border-bottom: 1px solid #f5f5f5;
	}
	.name-col {
		width: 100px;
		font-weight: 600;
		font-size: 0.9rem;
		color: #333;
	}
	.viz-col {
		flex: 1;
		padding: 0 12px;
	}

	/* Surname Viz Track */
	.viz-track {
		display: flex;
		height: 18px;
		width: 100%;
		border-radius: 4px;
		overflow: hidden;
		background: #f5f5f5; /* Empty track bg */
	}
	.viz-segment {
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden; /* Clip label if too small */
		min-width: 0;
		transition: width 0.5s ease-out;
	}
	.viz-segment.n {
		background: #004488;
	}
	.viz-segment.s {
		background: #cc6600;
	}

	.seg-label {
		color: white;
		font-size: 0.7rem;
		font-weight: 700;
		white-space: nowrap;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
		padding: 0 2px;
	}

	.count-col {
		width: 40px;
		text-align: right;
		font-weight: 700;
		font-size: 0.9rem;
		color: #1a1a1a;
	}

	/* Map */
	#map-container {
		height: 600px;
		width: 100%;
		border-radius: 8px;
		overflow: hidden;
		background: #f0f0f0;
	}
	:global(.map-popup) {
		font-family: 'Inter', sans-serif;
		min-width: 200px;
	}
	:global(.map-popup h3) {
		margin: 0 0 4px;
		font-size: 1rem;
		color: #b22222;
	}
	:global(.map-popup .stat) {
		font-weight: bold;
		font-size: 0.85rem;
		margin-bottom: 8px;
	}
	:global(.map-popup .divider) {
		height: 1px;
		background: #eee;
		margin: 8px 0;
	}
	:global(.map-popup .bio-list) {
		max-height: 150px;
		overflow-y: auto;
		font-size: 0.75rem;
		line-height: 1.4;
	}
	:global(.map-popup .bio-list p) {
		margin: 0 0 4px;
	}
</style>
