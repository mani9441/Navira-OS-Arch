class CapabilityResolver:

    def __init__(
        self,
        capability_registry
    ):
        self.capability_registry = (
            capability_registry
        )

    async def resolve(
        self,
        context
    ):
        raw_query = (
            context.inputs.get(
                "query",
                ""
            )
        )

        query_words = set(
            raw_query
            .lower()
            .replace("?", "")
            .replace("!", "")
            .split()
        )

        required_filters = (
            context.metadata
        )

        ranked_candidates = []

        for (
            name,
            cap_keywords
        ) in self.capability_registry.keywords.items():

            cap_metadata = (
                self.capability_registry
                .metadata
                .get(name, {})
            )

            if not all(
                cap_metadata.get(k) == v
                for k, v
                in required_filters.items()
            ):
                continue

            score = len(
                query_words.intersection(
                    cap_keywords
                )
            )

            if score > 0:

                ranked_candidates.append(
                    (
                        name,
                        score
                    )
                )

        if not ranked_candidates:
            raise ValueError(
                f"No capability matched "
                f"the keywords in query: "
                f"'{raw_query}'"
            )

        ranked_candidates.sort(
            key=lambda x: x[1],
            reverse=True
        )

        capability_name = (
            ranked_candidates[0][0]
        )

        capability = (
            self.capability_registry.get(
                capability_name
            )
        )

        if capability is None:
            raise ValueError(
                f"Capability "
                f"'{capability_name}' "
                f"not found"
            )

        return capability
    
    
# Vector Search
# Semantic Search
# Embeddings
# Metadata Filtering
# Capability Ranking