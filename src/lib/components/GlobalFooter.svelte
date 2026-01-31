<script>
	let shareText = 'Staffordshire War Dead';
	let copied = false;

	async function share() {
		if (navigator.share) {
			try {
				await navigator.share({
					title: 'Staffordshire War Dead',
					text: shareText,
					url: window.location.href
				});
			} catch (err) {
				console.error('Share failed:', err);
			}
		} else {
			try {
				await navigator.clipboard.writeText(window.location.href);
				copied = true;
				setTimeout(() => (copied = false), 2000);
			} catch (err) {
				console.error('Clipboard failed', err);
			}
		}
	}
</script>

<footer class="global-footer">
	<!-- Left: Link -->
	<a href="https://portfolio-three-livid-76.vercel.app/" class="footer-link left-link">
		<span>←</span> View All Doodles
	</a>

	<!-- Center: Credits -->
	<div class="credits">
		Designed & Built by <span class="highlight">David Elks</span>
	</div>

	<!-- Right: Share -->
	<button onclick={share} class="share-btn">
		{#if copied}
			<span>Copied!</span>
		{:else}
			<span>Share</span>
			<span class="arrow-icon">↗</span>
		{/if}
	</button>
</footer>

<style>
	:global(body) {
		margin: 0;
	}

	.global-footer {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		height: 40px; /* h-10 */
		background-color: rgba(15, 23, 42, 0.9); /* slate-900/90 */
		backdrop-filter: blur(4px); /* backdrop-blur-sm */
		z-index: 50;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 16px; /* px-4 */
		color: white;
		font-family: sans-serif;
		border-top: 1px solid rgba(51, 65, 85, 0.5); /* slate-700/50 */
		box-sizing: border-box;
	}

	.footer-link {
		font-size: 0.75rem; /* text-xs */
		font-weight: 500; /* font-medium */
		color: #cbd5e1; /* slate-300 */
		text-decoration: none;
		display: flex;
		align-items: center;
		gap: 0.25rem; /* gap-1 */
		transition: color 150ms;
	}
	.footer-link:hover {
		color: white;
	}

	.credits {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		font-size: 10px; /* text-[10px] */
		color: #94a3b8; /* slate-400 */
		font-weight: 300; /* font-light */
		letter-spacing: 0.025em; /* tracking-wide */
		white-space: nowrap;
	}
	@media (min-width: 768px) {
		.credits {
			font-size: 0.75rem; /* md:text-xs */
		}
	}
	.credits .highlight {
		color: #e2e8f0; /* slate-200 */
		font-weight: 500;
	}

	.share-btn {
		font-size: 0.75rem; /* text-xs */
		font-weight: 500;
		color: #cbd5e1; /* slate-300 */
		display: flex;
		align-items: center;
		gap: 0.25rem;
		background-color: rgba(30, 41, 59, 0.5); /* slate-800/50 */
		padding: 0.25rem 0.5rem; /* px-2 py-1 */
		border-radius: 0.25rem; /* rounded */
		border: none;
		cursor: pointer;
		transition:
			background-color 150ms,
			color 150ms;
	}
	.share-btn:hover {
		color: white;
		background-color: rgba(51, 65, 85, 1); /* slate-700 */
	}
	.arrow-icon {
		font-size: 10px;
		opacity: 0.7;
	}
</style>
