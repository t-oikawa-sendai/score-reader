# Restore this run in an isolated checkout

1. Obtain the repository commit recorded in source-state.json in a separate checkout.
2. Apply tracked.patch with `git apply --binary`.
3. Inspect the archive paths, then extract untracked.tar.gz into that checkout.
4. Verify every path in source-state.json against its SHA-256 (null means deleted).
5. Use the Python version in result.json and run the recorded suite. No third-party runtime dependencies are needed.

Do not apply this snapshot over existing work. Results are not part of the source snapshot and can be copied separately.
The patch represents the final worktree relative to HEAD, including staged and unstaged changes; staged-state identity is not required to reproduce execution.
