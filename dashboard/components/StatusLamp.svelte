<script>
	/**
	 * A console lamp. State is carried by an engraved word AND a drawn glyph,
	 * never by colour alone — the lamp colour is confirmation, not the message.
	 */

	/** nominal | caution | fault | off */
	export let state = 'nominal';
	/** Override the engraved word. */
	export let label = undefined;
	export let compact = false;

	const words = {
		nominal: 'Nominal',
		caution: 'Caution',
		fault: 'Fault',
		off: 'No data'
	};

	$: word = label ?? words[state] ?? state;
</script>

<span class="lamp-group" class:compact data-state={state}>
	<span class="lamp" aria-hidden="true">
		{#if state === 'nominal'}
			<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor">
				<circle cx="6" cy="6" r="5" stroke-width="1.5" />
				<path d="M3.5 6.2 5.2 8 8.5 4.4" stroke-width="1.5" stroke-linecap="square" />
			</svg>
		{:else if state === 'caution'}
			<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor">
				<path d="M6 1.2 11 10.5H1L6 1.2Z" stroke-width="1.5" stroke-linejoin="miter" />
				<path d="M6 4.8v2.4M6 8.8v.5" stroke-width="1.5" stroke-linecap="square" />
			</svg>
		{:else if state === 'fault'}
			<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor">
				<circle cx="6" cy="6" r="5" stroke-width="1.5" />
				<path d="M4 4l4 4M8 4l-4 4" stroke-width="1.5" stroke-linecap="square" />
			</svg>
		{:else}
			<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor">
				<circle cx="6" cy="6" r="5" stroke-width="1.5" />
				<path d="M3.4 6h5.2" stroke-width="1.5" stroke-linecap="square" />
			</svg>
		{/if}
	</span>
	<span class="word placard">{word}</span>
</span>

<style>
	.lamp-group {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		color: var(--lamp-off);
	}

	.lamp-group[data-state='nominal'] {
		color: var(--lamp-nominal);
	}
	.lamp-group[data-state='caution'] {
		color: var(--lamp-caution);
	}
	.lamp-group[data-state='fault'] {
		color: var(--lamp-fault);
	}

	.lamp {
		display: grid;
		place-items: center;
		width: 0.75rem;
		height: 0.75rem;
		flex-shrink: 0;
	}

	.word {
		color: currentColor;
		letter-spacing: 0.12em;
	}

	.compact .word {
		font-size: 0.625rem;
	}
</style>
