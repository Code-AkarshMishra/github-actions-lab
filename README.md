# github-actions-lab

A secure sandbox for scheduled GitHub Actions automation and development experiments. The scheduled task performs a repeatable repository health check and keeps the automation-file inventory below in sync. It does not invent work or create timestamp-only changes.

## Workflow architecture

- **Scheduled repository maintenance** runs daily and can also be started manually. It checks out the default branch, sets up Python 3.12, updates the managed file inventory only when the automation/test file set has changed, then runs the unit tests and formatting checks. It commits only a validated change to that inventory.
- **Manual repository check** is a read-only workflow for validating the repository without making a commit.
- Both workflows use GitHub-hosted runners, have a 10-minute timeout, and share a concurrency group so runs do not overlap.

The check uses only the Python standard library; there are no third-party Python dependencies to install or pin. GitHub Actions are referenced by major release tags (`actions/checkout@v4`, `actions/setup-python@v5`).

## Schedule and timezone

The scheduled workflow uses `17 9 * * *` (09:17 UTC daily). Change the `cron` expression in `.github/workflows/scheduled-check.yml` to adjust it. GitHub interprets scheduled cron expressions in UTC. Scheduled workflows can be delayed during periods of high load and are not guaranteed to start at the exact requested time.

## Permissions and automated commits

The scheduled workflow declares only `contents: write`, because it may commit the managed README inventory. GitHub provides the repository-scoped `GITHUB_TOKEN`; no personal access token or stored secret is used. The read-only manual workflow declares `contents: read`.

The scheduled script can change only the marked file-inventory section in this README. The workflow stages only `README.md`, rejects any staged path other than that file, runs tests and whitespace checks before committing, and skips the commit when there is no diff. It uses the `github-actions[bot]` author identity. Commits made with that bot identity are not represented as your personal contribution.

To run the scheduled workflow manually, open **Actions → Scheduled repository maintenance → Run workflow**. For a read-only validation, use **Actions → Manual repository check → Run workflow**. Each run's steps, logs, and summary are available from the workflow run page.

## Local checks

From the repository root, run:

```sh
python scripts/scheduled_check.py --check
python -m unittest discover -s tests -v
python -m tabnanny scripts tests
git diff --check
```

Use `python scripts/scheduled_check.py --update` to refresh the inventory locally when adding or removing workflow, script, or test files. Review and commit the resulting documentation change normally.

## Inspecting failures

Open the failed run under the repository's **Actions** tab and expand the failing step. The script prints timestamped messages indicating whether the inventory is current or was updated; unit-test output identifies failing tests. A stale inventory in the read-only workflow is an error and can be corrected with the local `--update` command or by starting the scheduled maintenance workflow.

## Disabling automation

To pause all automation, go to **Actions**, select a workflow, open its **…** menu, and choose **Disable workflow**. To stop only daily runs while keeping manual runs available, remove the `schedule` trigger from `.github/workflows/scheduled-check.yml`. Re-enable the workflow or restore the trigger to resume.

## Contribution eligibility and limitations

Private repository contributions can be shown on your profile by enabling **Include private contributions** in your GitHub profile's **Contributions & activity** settings. Personal commits generally need to be on the default branch (or `gh-pages`) and use an email address verified and associated with your GitHub account to be attributed to you. The automation uses GitHub's bot identity, so it does not claim your authorship or promise contribution credit. Private contribution details remain private.

This lab does not generate AI code, modify application logic, or make changes outside this repository. Its only automatic write is a deterministic documentation inventory update; it does not promise a contribution streak. Workflow failures, scheduling delays, GitHub contribution eligibility rules, and bot attribution can all prevent a run from producing a contribution on your profile.

## Maintained automation and test files

<!-- BEGIN AUTOMATED FILE INVENTORY -->
### Automation and test files

This list is synchronized by `scripts/scheduled_check.py`.

- `.github/workflows/manual-check.yml`
- `.github/workflows/scheduled-check.yml`
- `scripts/scheduled_check.py`
- `tests/test_scheduled_check.py`
<!-- END AUTOMATED FILE INVENTORY -->
