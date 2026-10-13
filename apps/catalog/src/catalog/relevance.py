"""How a browse list is ordered: by the published topic score."""

#: The score the harvester publishes, HIGHER IS BETTER. Ordering reads this and
#: never a tier name: the harvester owns that vocabulary, and a rename or a new
#: tier there must not need a release here.
TOPIC_SCORE_FIELD = "goat:topicRelevanceScore"

#: What an unscored row gets: the bottom of the published scale. Nothing known
#: is worth no more than known-to-be-marginal, and no less.
UNGRADED_RELEVANCE = 1

RELEVANCE_RANK_SQL = f'COALESCE("{TOPIC_SCORE_FIELD}", {UNGRADED_RELEVANCE})'

#: How much ground a row covers, the tiebreak behind the topic score. Read off
#: the footprint: an envelope over-claims, and a table has none and scores 0.
BBOX_AREA_SQL = "COALESCE(ST_Area(geometry), 0)"
