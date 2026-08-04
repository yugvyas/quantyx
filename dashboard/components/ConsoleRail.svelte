<script>
	import { base } from '$app/paths';

	export let currentPath = '';

	const stations = [
		{ label: 'Status', href: '/' },
		{ label: 'Skills', href: '/skills' },
		{ label: 'Compensation', href: '/compensation' },
		{ label: 'Companies', href: '/companies' },
		{ label: 'Postings', href: '/postings' },
		{ label: 'Method', href: '/methodology' }
	];

	// Trailing slashes vary between dev and the static build; normalize so the
	// active station does not silently fall through on the deployed site.
	const normalize = (p) => (p || '/').replace(/\/+$/, '') || '/';

	$: here = normalize(currentPath.replace(base, ''));
	$: isActive = (href) => normalize(href) === here;

	let open = false;

	// Evidence's own switcher lives in the header, which this shell hides — so
	// without this control the authored daylight register has no route to a
	// visitor. Evidence observes html[data-theme] and syncs its store from it,
	// so setting the attribute is the supported path, not a workaround.
	let theme = 'dark';

	if (typeof document !== 'undefined') {
		theme = document.documentElement.getAttribute('data-theme') ?? 'dark';
	}

	const toggleTheme = () => {
		theme = theme === 'dark' ? 'light' : 'dark';
		document.documentElement.setAttribute('data-theme', theme);
	};
</script>

<div class="console-rail">
	<div class="rail-inner">
		<a class="designation" href={`${base}/`}>
			<span class="mark" aria-hidden="true">
				<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor">
					<rect x="1.5" y="1.5" width="13" height="13" stroke-width="1.25" />
					<path d="M1.5 8h4M10.5 8h4M8 1.5v4M8 10.5v4" stroke-width="1.25" />
					<circle cx="8" cy="8" r="2.25" stroke-width="1.25" />
				</svg>
			</span>
			<span class="wordmark">quantyx</span>
		</a>

		<button
			class="lamp-switch"
			type="button"
			on:click={toggleTheme}
			aria-label={theme === 'dark' ? 'Switch to daylight register' : 'Switch to console register'}
			title={theme === 'dark' ? 'Daylight' : 'Console'}
		>
			<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor">
				{#if theme === 'dark'}
					<circle cx="8" cy="8" r="3.25" stroke-width="1.25" />
					<path
						d="M8 1v1.75M8 13.25V15M15 8h-1.75M2.75 8H1M12.95 3.05l-1.24 1.24M4.29 11.71l-1.24 1.24M12.95 12.95l-1.24-1.24M4.29 4.29 3.05 3.05"
						stroke-width="1.25"
						stroke-linecap="square"
					/>
				{:else}
					<path
						d="M13.4 9.6A5.6 5.6 0 0 1 6.4 2.6a5.75 5.75 0 1 0 7 7Z"
						stroke-width="1.25"
						stroke-linejoin="round"
					/>
				{/if}
			</svg>
		</button>

		<button
			class="rail-toggle placard"
			aria-expanded={open}
			aria-controls="rail-stations"
			on:click={() => (open = !open)}
		>
			{open ? 'Close' : 'Stations'}
		</button>

		<nav id="rail-stations" class="stations" class:open aria-label="Console stations">
			{#each stations as station}
				<a
					class="station placard"
					class:active={isActive(station.href)}
					href={`${base}${station.href}`}
					aria-current={isActive(station.href) ? 'page' : undefined}
					on:click={() => (open = false)}
				>
					{station.label}
				</a>
			{/each}
		</nav>
	</div>
</div>

<style>
	.rail-inner {
		max-width: 78rem;
		margin-inline: auto;
		padding-inline: 1.5rem;
		height: 3.25rem;
		display: flex;
		align-items: center;
		gap: 2rem;
	}

	.designation {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		text-decoration: none;
		color: var(--ink);
		flex-shrink: 0;
	}

	.mark {
		display: grid;
		place-items: center;
		width: 1.5rem;
		height: 1.5rem;
		color: var(--lamp-caution);
	}

	.wordmark {
		font-family: var(--font-placard);
		font-size: 0.9375rem;
		font-weight: 700;
		letter-spacing: 0.02em;
	}

	.stations {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		margin-left: auto;
	}

	.station {
		padding: 0.4rem 0.7rem;
		color: var(--ink-faint);
		text-decoration: none;
		border: 1px solid transparent;
		border-radius: 2px;
		transition: color 140ms ease-out, border-color 140ms ease-out;
	}

	.station:hover {
		color: var(--ink);
		border-color: var(--rule);
	}

	/* The active station is engraved, not merely tinted: identity never rests
	   on colour alone. */
	.station.active {
		color: var(--ink);
		border-color: var(--rule-strong);
		background: var(--panel-inset);
	}

	.lamp-switch {
		margin-left: auto;
		display: grid;
		place-items: center;
		width: 2rem;
		height: 2rem;
		background: transparent;
		border: 1px solid var(--rule);
		border-radius: 2px;
		color: var(--ink-faint);
		cursor: pointer;
		flex-shrink: 0;
		transition: color 140ms ease-out, border-color 140ms ease-out;
	}

	.lamp-switch:hover {
		color: var(--lamp-caution);
		border-color: var(--rule-strong);
	}

	/* Once the switch owns the auto margin, the stations sit next to it. */
	.stations {
		margin-left: 0.75rem;
	}

	.rail-toggle {
		display: none;
		margin-left: 0.75rem;
		background: var(--panel-raised);
		border: 1px solid var(--rule-strong);
		border-radius: 2px;
		padding: 0.4rem 0.7rem;
		color: var(--ink);
		cursor: pointer;
	}

	@media (max-width: 800px) {
		.rail-inner {
			padding-inline: 1rem;
			gap: 1rem;
		}

		.rail-toggle {
			display: block;
		}

		.stations {
			position: absolute;
			inset-inline: 0;
			top: 3.25rem;
			margin: 0;
			flex-direction: column;
			align-items: stretch;
			gap: 0;
			background: var(--panel-inset);
			border-bottom: 1px solid var(--rule-strong);
			display: none;
		}

		.stations.open {
			display: flex;
		}

		.station {
			padding: 0.85rem 1rem;
			border: 0;
			border-top: 1px solid var(--rule);
		}

		.station.active {
			background: var(--panel-raised);
		}
	}
</style>
