<script>
	/**
	 * A section of the console face: engraved placard cut into a hairline rule,
	 * an optional readable statement of what the section is for, then content.
	 *
	 * The placard is the section's own label — never an eyebrow above a
	 * separate heading.
	 */
	export let label;
	export let intro = undefined;
	/** Right-aligned annotation on the rule, e.g. a count or a timestamp. */
	export let annotation = undefined;
</script>

<section>
	<div class="engraved-rule">
		<h2 class="placard label">{label}</h2>
		{#if annotation}
			<span class="readout annotation">{annotation}</span>
		{/if}
	</div>

	{#if intro}
		<p class="intro">{intro}</p>
	{/if}

	<slot />
</section>

<style>
	.label {
		margin: 0;
		color: var(--ink);
		font-size: 0.75rem;
		letter-spacing: 0.16em;
	}

	.annotation {
		font-size: 0.6875rem;
		color: var(--ink-faint);
		order: 3;
		flex-shrink: 0;
	}

	.intro {
		margin: 0 0 1.5rem;
		max-width: 62ch;
		font-size: 0.9375rem;
		line-height: 1.7;
		color: var(--ink-dim);
	}
</style>
