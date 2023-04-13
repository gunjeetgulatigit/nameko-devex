<script context="module" lang="ts">
	import { ROUTES } from './routes'
</script>

<svelte:head>
	<title>Home</title>
</svelte:head>

<main>
	{#each Object.entries(ROUTES) as [name, route]}
		<a class="mx-2 text-blue-400 underline" href={route}>{name}</a>
	{/each}
</main>