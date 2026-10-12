"""Names goatlib's Postgres sessions carry in pg_stat_activity.

Operators see which part of GOAT holds a connection by its application_name.
"""

# Analytics tools and workflows, run as Windmill jobs.
TOOLS_APPLICATION_NAME = "goat-tools"
# Scheduled maintenance and housekeeping tasks.
TASKS_APPLICATION_NAME = "goat-tasks"
