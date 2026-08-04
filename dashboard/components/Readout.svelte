<script>
	/**
	 * A single value sunk into a recessed well, the way a console shows a live
	 * quantity: engraved placard label above, tabular readout below, unit set
	 * apart so the number itself stays scannable.
	 *
	 * Deliberately not the big-number/small-label stat card: the well, the
	 * engraved label and the scale tick are the world's own vocabulary.
	 */
	export let label;
	export let value;
	/** Small trailing unit, e.g. "roles", "days". */
	export let unit = undefined;
	/** Secondary line under the value, for provenance or qualification. */
	export let note = undefined;
	/** Emphasize this as the board's headline figure. */
	export let lead = false;

	const format = (v) => {
		if (v === null || v === undefined || v === '') return '—';
		const n = typeof v === 'number' ? v : Number(v);
		return Number.isFinite(n) ? n.toLocaleString('en-IN') : String(v);
	};
</script>

<div class="well readout-well" class:lead>
	<div class="placard">{label}</div>
	<div class="value-row">
		<span class="readout value">{format(value)}</span>
		{#if unit}<span class="unit">{unit}</span>{/if}
	</div>
	{#if note}<div class="note">{note}</div>{/if}
</div>

<style>
	.readout-well {
		padding: 0.875rem 1rem 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
		position: relative;
	}

	/* Engraved scale tick — the mark a panel gauge is read against. */
	.readout-well::before {
		content: '';
		position: absolute;
		top: 0;
		left: 1rem;
		width: 1.75rem;
		height: 2px;
		background: var(--rule-strong);
	}

	.lead::before {
		background: var(--lamp-caution);
	}

	.value-row {
		display: flex;
		align-items: baseline;
		gap: 0.4rem;
	}

	.value {
		font-size: 1.75rem;
		font-weight: 500;
		line-height: 1;
	}

	.lead .value {
		font-size: 2.75rem;
		font-weight: 700;
	}

	.unit {
		font-family: var(--font-placard);
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--ink-faint);
	}

	.note {
		font-family: var(--font-placard);
		font-size: 0.75rem;
		line-height: 1.45;
		color: var(--ink-faint);
	}

	@media (max-width: 640px) {
		.lead .value {
			font-size: 2.25rem;
		}
	}
</style>
