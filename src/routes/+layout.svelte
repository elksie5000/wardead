<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import GlobalFooter from '$lib/components/GlobalFooter.svelte';
	import { injectAnalytics } from '@vercel/analytics/sveltekit';
	import { dev } from '$app/environment';

	injectAnalytics({ mode: dev ? 'development' : 'production' });

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}

<footer>
	<p>
		Check out my other project: <a href="https://baby-names-three.vercel.app/"
			>Baby Names Visualization</a
		>
	</p>
</footer>

<GlobalFooter />

<style>
	footer {
		margin-top: 48px;
		padding: 24px 24px 80px 24px;
		border-top: 1px solid #eee;
		text-align: center;
		color: #666;
		font-family: 'Inter', sans-serif;
	}

	footer a {
		color: #b22222;
		text-decoration: none;
		font-weight: 600;
	}

	footer a:hover {
		text-decoration: underline;
	}
</style>
