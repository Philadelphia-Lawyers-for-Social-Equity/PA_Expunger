## Overview

Provide an overview of the changes to be reviewed, the issue they are trying to solve, and anything to note as the reviewer goes through them.

### Does this close any currently open issues?

<!-- Change ### to #[number of issue], e.g. #1 -->
Closes ###

### Testing Instructions

- Provide instructions to test the changes
- Bullet lists are helpful
- [ ] Checkboxes also  help for specific tasks
- Create tests for your contribuition. These tests should demonstrate functionality, and tests that fail intenionally should be added. 
- The "happy path" is helpful, but knowing how the changes respond to errors is extra helpful

### Self check
- [ ] Have the guidelines detiled in the contribuitng.m been followed
- [ ] Can someone who new to the project read the overview and come away with what the problem os and how its being solved
- [ ] Can the code handle exceptions and errors if design by contract is violated
-[ ] Make sure reviewers know to review this by assigning either the team lead or two team members in the 'reviewers' tab in the sidebar or under the PR text depending on your view.


### Before merging

- [ ] PR has been reviewed and approved
- [ ] Branch has been rebased on `develop` (or the branch being merged to). [See here for rebase instructions](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/blob/develop/CONTRIBUTING.md#reviewed-work)
