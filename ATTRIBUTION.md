# Attribution and Upstream References

Ultima-Graph synthesizes and builds upon the foundational research, algorithms, and architectures established by two open-source software intelligence projects:

---

## 1. CodeGraph

* **Repository:** [https://github.com/colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
* **Author / Maintainer:** Colby McHenry
* **License:** MIT License (Copyright (c) 2026 Colby Mchenry)
* **Foundational Concepts & Architectural Inspiration:**
  * **Deterministic AST Code Indexing:** High-speed, local-first AST parsing using Tree-sitter without LLM extraction overhead.
  * **FTS5 & Sub-Identifier Vocabulary:** SQLite WAL storage with `name_segment_vocab` decomposition (splitting camelCase, PascalCase, and snake_case into searchable tokens) enabling natural-language symbol lookups without embedding vectors.
  * **Reference Resolution Engine:** Advanced heuristics for resolving framework routes (Express, FastAPI, Django, Rails, Spring, etc.), client navigation (Next.js, React Router), and cross-tier network bridges (`fetch`/`axios` to backend endpoints).
  * **Single-Shot Context Delivery:** Consolidated query patterns returning line-numbered snippets, call paths, and blast radius in a single call to prevent context churn.
  * **Impact & Test Mapping:** Transitive caller-tree analysis and `affected` test selection from git diffs.

---

## 2. Graphify

* **Repository:** [https://github.com/Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)
* **Author / Maintainer:** Safi Shamsi / Graphify Labs
* **License:** Apache License 2.0 / MIT License (Copyright (c) 2026 Safi Shamsi)
* **Foundational Concepts & Architectural Inspiration:**
  * **Multimodal Knowledge Graph Construction:** Unified knowledge extraction spanning polyglot codebases (50+ extensions), technical documentation, research papers, diagrams, and transcribed media.
  * **Network Science Analytics:** Community detection utilizing Leiden clustering algorithms, cohesion scoring, and modularity quantification.
  * **Centrality & God-Node Detection:** Degree centrality analysis with standard-library noise filtering to isolate true architectural hubs and single points of failure.
  * **Surprising Connections:** Boundary-crossing topological edge analysis identifying unexpected coupling between disjoint subsystems.
  * **Confidence Scoring Rubric:** Explicit relationship confidence tiering (`EXTRACTED`, `INFERRED`, `AMBIGUOUS`).

---

## License Notices

Both upstream projects are distributed under permissive open-source licenses (MIT and Apache 2.0). Ultima-Graph incorporates the operational workflows, schemas, prompt protocols, and tool routing patterns inspired by these systems while providing an integrated, cost-governed execution environment for AI agents.

Copies of the original licenses are maintained in their respective source repositories linked above.
