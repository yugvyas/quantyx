<script>
	import StatusLamp from './StatusLamp.svelte';

	/**
	 * The four ingest channels, each individually lamped. A channel that
	 * reported this run is nominal; one that contributed nothing is off — which
	 * is exactly what `assert_no_source_disappeared` watches for.
	 */

	/** Rows of { source, postings, companies }. */
	export let data = [];

	const CHANNELS = [
		{ id: 'adzuna', name: 'Adzuna', detail: 'India market · keyed API' },
		{ id: 'greenhouse', name: 'Greenhouse', detail: 'Company boards · no auth' },
		{ id: 'lever', name: 'Lever', detail: 'Company boards · no auth' },
		{ id: 'ashby', name: 'Ashby', detail: 'Company boards · structured pay' }
	];

	$: rows = CHANNELS.map((c) => {
		const hit = (data ?? []).find((d) => String(d.source).toLowerCase() === c.id);
		const postings = hit ? Number(hit.postings) : 0;
		return { ...c, postings, state: postings > 0 ? 'nominal' : 'off' };
	});
</script>

<div class="strip" role="list">
	{#each rows as row (row.id)}
		<div class="channel" role="listitem">
			<div class="head">
				<span class="name">{row.name}</span>
				<StatusLamp state={row.state} compact={true} label={row.state === 'nominal' ? 'Live' : 'Silent'} />
			</div>
			<div class="count readout">{row.postings.toLocaleString('en-IN')}</div>
			<div class="detail">{row.detail}</div>
		</div>
	{/each}
</div>

<style>
	.strip {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1px;
		background: var(--rule);
		border: 1px solid var(--rule);
		border-radius: 2px;
		overflow: hidden;
	}

	.channel {
		background: var(--panel-raised);
		padding: 0.875rem 1rem 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.name {
		font-family: var(--font-placard);
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--ink);
	}

	.count {
		font-size: 1.25rem;
		font-weight: 500;
		line-height: 1;
	}

	.detail {
		font-size: 0.6875rem;
		line-height: 1.4;
		color: var(--ink-faint);
	}

	@media (max-width: 860px) {
		.strip {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (max-width: 460px) {
		.strip {
			grid-template-columns: 1fr;
		}
	}
</style>
