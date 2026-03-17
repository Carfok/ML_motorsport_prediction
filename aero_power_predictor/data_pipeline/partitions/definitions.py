from dagster import DailyPartitionsDefinition

# Partición diaria para la temporada 2026
season_2026_partitions = DailyPartitionsDefinition(start_date="2026-01-01")
