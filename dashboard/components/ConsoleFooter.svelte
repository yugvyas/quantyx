<script>
	const repo = 'https://github.com/yugvyas/quantyx';
</script>

<footer>
	<div class="footer-inner">
		<div class="plate">
			<span class="placard">Built by</span>
			<span class="name">Yug Vyas</span>
		</div>

		<a class="repo" href={repo} rel="noopener">
			<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" fill="currentColor">
				<path
					d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
					0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01
					1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95
					0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.42 7.42 0 0 1 2-.27c.68 0
					1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0
					3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01
					8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"
				/>
			</svg>
			<span class="placard">Source</span>
			<span class="path">github.com/yugvyas/quantyx</span>
		</a>
	</div>
</footer>

<style>
	footer {
		border-top: 1px solid var(--rule-strong);
		background: var(--panel-inset);
	}

	.footer-inner {
		max-width: 78rem;
		margin-inline: auto;
		padding: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1.5rem;
		flex-wrap: wrap;
	}

	.plate {
		display: flex;
		align-items: baseline;
		gap: 0.625rem;
	}

	.name {
		font-family: var(--font-placard);
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--ink);
	}

	.repo {
		display: inline-flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.5rem 0.875rem;
		border: 1px solid var(--rule-strong);
		border-radius: 2px;
		background: var(--panel-raised);
		color: var(--ink);
		text-decoration: none;
		transition: border-color 140ms ease-out, background 140ms ease-out;
	}

	.repo:hover {
		border-color: var(--lamp-caution);
		background: var(--panel);
	}

	.path {
		font-family: var(--font-readout);
		font-size: 0.75rem;
		color: var(--ink-dim);
	}

	@media (max-width: 560px) {
		.path {
			display: none;
		}
	}
</style>
