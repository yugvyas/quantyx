<script>
	import StatusLamp from './StatusLamp.svelte';

	/**
	 * The gate. Four drift tests run before every deploy; if any returns rows
	 * the workflow halts BEFORE publishing and the previous site stays live.
	 *
	 * Named for what it is rather than for a GO/NO-GO poll: it renders no live
	 * verdict lamps, deliberately. Nothing here polls a running system.
	 *
	 * This module deliberately does NOT claim to poll anything live. Its
	 * verdict is an inference with one premise, printed alongside it: a build
	 * that fails these tests never reaches a browser, so a reader seeing this
	 * page at all is seeing a run where all four passed. Lamps that could only
	 * ever render GO would be decoration; the halt case is shown instead, as
	 * the worked example it deserves.
	 */
	export let lastRun = undefined;
	/** Days of history recorded, from agg_pipeline_stats. */
	export let daysOfHistory = undefined;

	// The volume test compares today against a trailing seven-day average, so
	// it genuinely no-ops until seven days exist — a real machine condition,
	// and the one place caution belongs rather than being decoration.
	const ARMS_AT = 7;
	$: dormant = Number.isFinite(Number(daysOfHistory)) && Number(daysOfHistory) < ARMS_AT;

	// The mart column arrives as a Date; interpolating it raw prints
	// "Tue Aug 04 2026 05:30:00 GMT+0530 (India Standard Time)".
	const asDate = (v) => {
		if (!v) return undefined;
		const d = v instanceof Date ? v : new Date(v);
		return Number.isNaN(d.valueOf()) ? String(v) : d.toISOString().slice(0, 10);
	};

	$: runStamp = asDate(lastRun);

	const checks = [
		{
			name: 'assert_volume_not_collapsed',
			watches: 'Today’s volume against its trailing seven-day average',
			armsAt: true
		},
		{
			name: 'assert_no_source_disappeared',
			watches: 'A channel that goes silent while the others carry the total'
		},
		{
			name: 'assert_required_fields_present',
			watches: 'A field that stops being populated after an upstream rename'
		},
		{
			name: 'assert_compensation_is_coherent',
			watches: 'Pay figures that cannot be true'
		}
	];
</script>

<div class="gate">
	<div class="gate-head">
		<span class="placard">Pre-publish checks</span>
	</div>

	<ul class="checks">
		{#each checks as check}
			<li>
				<span class="body">
					<span class="name readout">{check.name}</span>
					<span class="watches">{check.watches}</span>
				</span>
				{#if check.armsAt && dormant}
					<StatusLamp state="caution" label="Dormant" compact={true} />
				{:else}
					<StatusLamp state="nominal" label="Armed" compact={true} />
				{/if}
			</li>
		{/each}
	</ul>

	{#if dormant}
		<p class="dormant-note">
			<StatusLamp state="caution" label="Not yet armed" compact={true} />
			<span class="measure">
				The volume check needs {ARMS_AT} days of history to have a trailing average to compare
				against; {daysOfHistory} exist so far, so it passes without testing anything. Stating that
				is cheaper than a green lamp that means nothing.
			</span>
		</p>
	{/if}

	<div class="verdict">
		<div class="outcome">
			<StatusLamp state="nominal" label="Published" />
			<p>
				All four passed{runStamp ? ` on ${runStamp}` : ''}, which is the only reason this page
				updated.
			</p>
		</div>
		<div class="outcome">
			<StatusLamp state="fault" label="Halted" />
			<p>
				Any one of them returning a row stops the deploy, files an issue, and leaves the previous
				dashboard live — so a stale page, not a wrong one, is what failure looks like here.
			</p>
		</div>
	</div>

	<p class="proof">
		<span class="measure">
			<code>scripts/verify_drift_detection.sh</code> corrupts the sample dataset on purpose in CI
			and asserts these tests fail. A test never observed failing is not evidence of anything.
		</span>
	</p>
</div>

<style>
	.gate {
		border: 1px solid var(--rule);
		border-radius: 2px;
		background: var(--panel-raised);
	}

	.gate-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--rule);
		background: var(--panel-inset);
	}

	.checks {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.checks li {
		display: grid;
		grid-template-columns: 1fr auto;
		align-items: center;
		gap: 1rem;
		padding: 0.7rem 1rem;
		border-bottom: 1px solid var(--rule);
	}

	.body {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		min-width: 0;
	}

	.name {
		font-size: 0.75rem;
		color: var(--ink);
		overflow-wrap: anywhere;
	}

	.watches {
		font-family: var(--font-placard);
		font-size: 0.75rem;
		line-height: 1.45;
		color: var(--ink-dim);
	}

	/* Both outcomes shown side by side: the lamp system has three states and
	   this is where the other one earns its place. */
	.verdict {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1px;
		background: var(--rule);
		border-top: 1px solid var(--rule);
	}

	.outcome {
		background: var(--panel-inset);
		padding: 0.875rem 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.45rem;
	}

	.outcome p {
		max-width: none;
		margin: 0;
		font-size: 0.8125rem;
		line-height: 1.6;
		color: var(--ink-dim);
	}

	.dormant-note {
		/* .markdown p caps at 68ch, which ends this row's background mid-module. */
		max-width: none;
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.5rem;
		margin: 0;
		padding: 0.75rem 1rem;
		border-top: 1px solid var(--rule);
		background: var(--panel-inset);
		font-size: 0.8125rem;
		line-height: 1.6;
		color: var(--ink-dim);
	}

	.proof {
		max-width: none;
		margin: 0;
		padding: 0.75rem 1rem;
		border-top: 1px solid var(--rule);
		font-size: 0.75rem;
		line-height: 1.6;
		color: var(--ink-faint);
	}

	/* The row's plate spans its module; the text inside keeps the site measure.
	   Uncapping the paragraph itself traded a phantom cell for 100-char lines. */
	.measure {
		display: inline-block;
		max-width: 68ch;
	}

	.proof code {
		font-family: var(--font-readout);
		color: var(--ink-dim);
	}

	@media (max-width: 640px) {
		.verdict {
			grid-template-columns: 1fr;
		}
	}
</style>
