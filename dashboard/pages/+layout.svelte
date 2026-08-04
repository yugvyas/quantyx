<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	import { base } from '$app/paths';
	import { page } from '$app/stores';
	import ConsoleRail from '../components/ConsoleRail.svelte';
	import ConsoleFooter from '../components/ConsoleFooter.svelte';

	export let data;

	// Svelte strips ordinary HTML comments at compile time, so the direction
	// contract is injected as raw markup to guarantee it survives the
	// production build and stays auditable in the shipped HTML.
	const contract = `<!--
THESIS: not a dashboard — a console watching an unattended machine, whose
headline is that it can refuse to publish. Refuses the SaaS-card arrangement
(sidebar + rounded cards + Inter + blue accent) that Evidence ships by default,
and equally refuses its opposite, the green-on-black terminal.
OWN-WORLD: matte console panel (#101619) machined with faint vertical rules;
modules bolted into the face, live values sunk into recessed wells; engraved
placard capitals (Archivo, tracked 0.14em) against tabular readouts (JetBrains
Mono); hairline engraved rules; status lamps in nominal/caution/fault used only
for state, never decoration.
STORY: the visitor sees a machine reporting its own condition, understands it
ran this morning without a human, learns it halts rather than publish bad data,
and leaves for the repository.
FIRST VIEWPORT: full-width status board — designation on the rail, LAST RUN
readout in the board's state column; a four-channel source strip, each channel
individually lamped; the four pre-publish checks, each lamped armed or dormant,
with both outcomes shown; primary action (the repository) at the board's right.
FORM: mission-control telemetry console; candidate 6 of the grounded list;
seed key 30ac0dbd.
FINISH: unreviewed and undocumented is unfinished; this build ends with the
finish review, the verdict, and DESIGN.md.
-->`;
</script>

<svelte:head>
	<link rel="stylesheet" href={`${base}/fonts/fonts.css`} />
	<link rel="stylesheet" href={`${base}/console.css`} />
	<link
		rel="preload"
		as="font"
		type="font/woff2"
		href={`${base}/fonts/Archivo-5.woff2`}
		crossorigin="anonymous"
	/>
	<link
		rel="preload"
		as="font"
		type="font/woff2"
		href={`${base}/fonts/JetBrainsMono-1.woff2`}
		crossorigin="anonymous"
	/>
</svelte:head>

{@html contract}

<EvidenceDefaultLayout
	{data}
	hideSidebar={true}
	hideHeader={true}
	hideBreadcrumbs={true}
	hideTOC={true}
	fullWidth={true}
	builtWithEvidence={false}
>
	<div slot="content" class="console-shell">
		<ConsoleRail currentPath={$page.url.pathname} />

		<main class="console-frame pb-24 pt-10">
			<slot />
		</main>

		<ConsoleFooter />
	</div>
</EvidenceDefaultLayout>

<style>
	main {
		max-width: 78rem;
		margin-inline: auto;
		padding-inline: 1.5rem;
	}

	@media (max-width: 640px) {
		main {
			padding-inline: 1rem;
		}
	}
</style>
