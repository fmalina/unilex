CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX concept_name_trigram_idx ON concepts USING gin (name gin_trgm_ops);
CREATE INDEX concept_description_trigram_idx ON concepts USING gin (description gin_trgm_ops);
CREATE INDEX concept_node_id_trigram_idx ON concepts USING gin (node_id gin_trgm_ops);
