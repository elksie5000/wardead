<script>
	import { onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import { fade } from 'svelte/transition';
	export let data;

	$: ({ mapData, rankStats, timeline, surnames } = data);

	// --- Surname Filtering & Animation Logic ---
	let surnameFilter = 'total_count'; // Options: total_count, north_staffs_count, south_staffs_count
	$: displaySurnames = [...surnames]
		.sort((a, b) => b[surnameFilter] - a[surnameFilter])
		.slice(0, 20);

	// --- Timeline Tooltip Logic ---
	let hoveredDay = null;

	onMount(async () => {
		const L = await import('leaflet');
		const map = L.map('map-container').setView([50.5, 3.0], 7);

		L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}{r}.png', {
			attribution:
				'&copy; Stadia Maps, &copy; Stamen Design, Data: Commonwealth War Grave Commission'
		}).addTo(map);

		mapData.forEach((site) => {
			if (site.latitude && site.longitude) {
				const radius = Math.sqrt(site.num_commemorated || 1) * 200;
				const circle = L.circle([site.latitude, site.longitude], {
					color: '#b22222',
					fillColor: '#b22222',
					fillOpacity: 0.5,
					radius: radius
				}).addTo(map);

				circle.bindPopup(`
                    <div style="max-height: 200px; overflow-y: auto;">
                        <strong>${site.cemetery_name}</strong><br/>
                        ${site.num_commemorated} fatalities.<hr/>
                        ${site.fallen_list.map((f) => `<p style="font-size:0.75rem">${f.bio}</p>`).join('')}
                    </div>
                `);
			}
		});
	});
</script>

<svelte:head>
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<main class="dashboard">
	<section class="card full-width">
		<header class="chart-header">
			<h2>Staffordshire Regiments: Daily Casualty Timeline (1914-1918)</h2>
			{#if hoveredDay}
				<div class="tooltip-display" transition:fade>
					<strong>{hoveredDay.iso_date}</strong>:
					<span class="t-total">{hoveredDay.total_deaths} Total</span> |
					<span class="t-north">{hoveredDay.north_staffs} North</span> |
					<span class="t-south">{hoveredDay.south_staffs} South</span>
				</div>
			{/if}
		</header>

		<div class="timeline-viz">
			<svg viewBox="0 0 1400 300" preserveAspectRatio="none">
				{#each timeline as day, i}
					<g on:mouseenter={() => (hoveredDay = day)} on:mouseleave={() => (hoveredDay = null)}>
						<rect
							x={(i / timeline.length) * 1400}
							y={300 - ((day.south_staffs + day.north_staffs) / 550) * 300}
							width={1400 / timeline.length}
							height={(day.south_staffs / 550) * 300}
							fill="#cc6600"
						/>
						<rect
							x={(i / timeline.length) * 1400}
							y={300 - (day.north_staffs / 550) * 300}
							width={1400 / timeline.length}
							height={(day.north_staffs / 550) * 300}
							fill="#004488"
						/>
					</g>
				{/each}
			</svg>
			<div class="x-axis">
				<span>1914</span><span>1915</span><span>1916</span><span>1917</span><span>1918</span>
			</div>
		</div>
	</section>

	<div class="two-col">
		<section class="card">
			<h3>Casualties by Rank</h3>
			<div class="rank-chart">
				{#each rankStats.slice(0, 12) as r}
					<div class="rank-bar-row">
						<span class="rank-name">{r.rank}</span>
						<div class="rank-bar-container">
							<div
								class="rank-bar"
								style="width: {(r.total_deaths / rankStats[0].total_deaths) * 100}%"
							>
								<span class="rank-label">{r.total_deaths}</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</section>

		<section class="card">
			<div class="flex-between">
				<h3>Top 20 Surnames</h3>
				<select bind:value={surnameFilter}>
					<option value="total_count">Sort by All</option>
					<option value="north_staffs_count">Sort by North Staffs</option>
					<option value="south_staffs_count">Sort by South Staffs</option>
				</select>
			</div>
			<div class="surname-list">
				{#each displaySurnames as s (s.surname)}
					<div class="surname-row" animate:flip={{ duration: 400 }}>
						<span class="s-name">{s.surname}</span>
						<div class="s-bars">
							<div class="s-bar north" style="width: {(s.north_staffs_count / 210) * 100}%"></div>
							<div class="s-bar south" style="width: {(s.south_staffs_count / 210) * 100}%"></div>
							<span class="s-val">{s[surnameFilter]}</span>
						</div>
					</div>
				{/each}
			</div>
		</section>
	</div>

	<div id="map-container" style="height: 600px; margin-top: 20px; border: 2px solid #000;"></div>
</main>

<style>
	.dashboard {
		padding: 20px;
		background: #fff;
		color: #000;
	}
	.full-width {
		grid-column: 1 / -1;
		margin-bottom: 20px;
	}
	.two-col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 20px;
	}
	.card {
		border: 1px solid #ddd;
		padding: 1.5rem;
		background: #fff;
	}

	/* Timeline */
	.timeline-viz {
		position: relative;
		height: 320px;
		border-bottom: 2px solid #000;
	}
	svg {
		width: 100%;
		height: 300px;
		display: block;
	}
	.x-axis {
		display: flex;
		justify-content: space-between;
		padding-top: 10px;
		font-weight: bold;
	}
	.tooltip-display {
		font-family: monospace;
		font-size: 1rem;
		color: #b22222;
	}

	/* Rank Bars */
	.rank-bar-row {
		display: flex;
		align-items: center;
		margin-bottom: 4px;
	}
	.rank-name {
		width: 120px;
		font-size: 0.8rem;
		text-align: right;
		margin-right: 10px;
	}
	.rank-bar-container {
		flex-grow: 1;
		background: #eee;
		height: 18px;
		position: relative;
	}
	.rank-bar {
		background: #444;
		height: 100%;
		display: flex;
		align-items: center;
		padding-left: 5px;
	}
	.rank-label {
		color: white;
		font-size: 0.7rem;
		font-weight: bold;
	}

	/* Surname Bars */
	.surname-row {
		display: flex;
		align-items: center;
		margin-bottom: 2px;
	}
	.s-name {
		width: 80px;
		font-size: 0.85rem;
	}
	.s-bars {
		flex-grow: 1;
		display: flex;
		align-items: center;
		height: 12px;
		gap: 2px;
	}
	.s-bar {
		height: 100%;
		transition: width 0.4s ease;
	}
	.north {
		background: #004488;
	}
	.south {
		background: #cc6600;
	}
	.s-val {
		font-size: 0.7rem;
		margin-left: 5px;
		color: #666;
	}
</style>
