# n8n Workflow Demo

This folder contains a simple n8n workflow concept for employee request routing.

The purpose is not to show a production workflow. It is included to demonstrate how the dashboard idea could be extended into real workflow automation.

## Demo logic

```text
Manual trigger
   ↓
Create demo request
   ↓
Check impact score
   ↓
If high impact: route for approval
   ↓
If lower priority: keep for review
```

## Possible real version

A real version could use:

- webhook from a request form
- Google Sheets or PostgreSQL as the tracker
- manager approval step
- email or Teams notification
- dashboard refresh
- monthly report summary
```

## Notes

The workflow uses fictional demo values only.