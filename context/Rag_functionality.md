# RAG Functionality Completion

In order to complete the Phase 1 functionality as per Overview.md, the following steps need to be completed:

1. Unblock NMS/ZMS API access — nothing else in Phase 1 moves without this
2. Add NMS_BASE_URL to config + env
3. Expand nms_client.py with real command methods once NMS endpoints are known
4. Rework POST /diagnostics/run into a proper context-capture pipeline
5. Add PATCH /cases/{case_id}/outcome for engineers to close sessions
6. Swap in real embeddings — pick a provider and wire it into embedding.py

The provider will be anthropic claude 