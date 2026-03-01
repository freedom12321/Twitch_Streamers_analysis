# Data Cleaning Report

## Dataset Snapshot
- Raw rows: 3,051,733
- Clean rows: 3,051,733
- Rows removed: 0
- Unique channels: 162,625
- Unique viewers (sampled IDs): 6,148

## Missingness
- language_cluster_id: 0
- session_id: 0
- channel_login: 0
- viewer_id: 0
- engagement_rank: 0

## Outlier Checks
- Viewer IDs outside 0-6147: 0
- Engagement ranks outside 1-6148: 0

## Notes
- Standardized channel logins to lowercase and trimmed whitespace.
- Removed duplicate rows (if any) to avoid double-counting interactions.
- Filtered implausible viewer/engagement ids outside the observed ID range.