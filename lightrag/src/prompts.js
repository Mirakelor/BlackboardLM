const ENTITY_EXTRACTION_PROMPT = `---Role---
You are an expert knowledge graph builder. Extract entities and relationships from the text.

---Goal---
Given a text chunk, identify ALL named entities (people, places, organizations, concepts, events, dates, technologies) and the relationships between them.

---Output Format---
Return a JSON object with "entities" and "relations":
{
  "entities": [
    {"name": "Entity", "type": "PERSON|ORGANIZATION|LOCATION|CONCEPT|EVENT|DATE|TECH", "description": "Brief description"}
  ],
  "relations": [
    {"source": "Entity A", "target": "Entity B", "keywords": "relationship", "weight": 1.0}
  ]
}

---Rules---
- Entity name under 60 chars, description under 120 chars
- Extract at least 3 entities per chunk
- Weight between 0.5 (weak) and 1.5 (strong)
- Return ONLY valid JSON, no other text.

---Text---
{text}`;

module.exports = { ENTITY_EXTRACTION_PROMPT };
