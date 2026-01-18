<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';

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

<style>
	footer {
		margin-top: 48px;
		padding: 24px;
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
