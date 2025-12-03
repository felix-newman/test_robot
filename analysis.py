import pstats

pstats.Stats("record.stats").sort_stats("cumulative").print_callees("save_episode")
