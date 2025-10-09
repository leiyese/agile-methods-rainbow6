# Semantisk PDF-chunker för juridiska dokument

Detta verktyg implementerar en specialiserad chunkning-strategi för juridiska/försäkringsdokument i PDF-format, med fokus på semantisk struktur snarare än godtyckliga token-gränser.

## Funktioner

- **Intelligent chunkning baserad på dokumentstruktur**: Följer dokumentets hierarki (kapitel, avsnitt, underavsnitt)
- **Bevarande av semantiska enheter**: Håller relaterat innehåll tillsammans
- **Metadataextrahering för varje chunk**: Avsnittskoder, rubriker, ämnestaggar, etc.
- **Tabelldetektering och -bevarande**: Tabeller hålls intakta
- **Hantering av korsreferenser**: Identifierar och bevarar viktiga korsreferenser

## Installation

1. Installera beroenden:

```bash
pip install -r scripts/requirements.txt
```

2. Ladda ner språkmodell för spaCy (om du vill använda NLP-funktioner):

```bash
python -m spacy download sv_core_news_sm  # Svenska
# eller
python -m spacy download en_core_web_sm   # Engelska (fallback)
```

## Användning

### Grundläggande användning

```bash
python scripts/pdf_chunker.py backend/rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf
```

Detta kommer att:
1. Extrahera text från PDF-filen
2. Skapa semantiska chunks enligt strategin
3. Spara chunks till en JSON-fil eller databasen (om tillgänglig)

### Avancerade alternativ

```bash
python scripts/pdf_chunker.py backend/rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf \
  --output output/chunks.json \
  --chunk-size 300 \
  --min-chunk 150 \
  --max-chunk 400 \
  --overlap 50 \
  --local
```

Parametrar:
- `--output`: Sökväg för utdata-JSON (valfritt)
- `--chunk-size`: Basstorlek för chunks i tokens (standard: 300)
- `--min-chunk`: Minsta chunkstorlek i tokens (standard: 150)
- `--max-chunk`: Största chunkstorlek i tokens (standard: 400)
- `--overlap`: Överlappningsstorlek i tokens (standard: 50)
- `--local`: Använd lokala embeddings istället för Gemini API
- `--test`: Testa chunkning utan att spara resultat
- `--verbose`: Visa detaljerad information om chunks vid testning

### Testning av chunkning

För att testa chunkning-strategin utan att spara resultaten:

```bash
python scripts/pdf_chunker.py backend/rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf --test
```

För att visa detaljerad information om de skapade chunks:

```bash
python scripts/pdf_chunker.py backend/rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf --test --verbose
```

Detta är användbart för att utvärdera och finjustera chunkning-strategin utan att behöva spara resultaten till en fil eller databas.

## Chunkning-strategi

Verktyget implementerar följande strategi för chunkning:

1. **Följer dokumentstruktur**: Chunks följer rubriker (A-F, med underpunkter) och behandlar tabeller som egna chunks.

2. **Rekommenderad chunk-storlek och överlapp**:
   - Basstorlek: 200-400 tokens per chunk
   - Överlapp: 40-60 tokens endast när man måste bryta mitt i ett längre avsnitt; annars 0
   - Kortavsnitt: Om ett avsnitt är <150 tokens — låt det vara en egen chunk

3. **Chunkar efter semantiska enheter**:
   - Rubrik + dess brödtext = 1 chunk (om det ryms inom 400 tokens)
   - Punktlistor under samma rubrik = i samma chunk om de hör ihop och ryms
   - Korsreferenser hålls inom samma chunk om möjligt

4. **Särskilda regler per kapitel/avsnitt**:
   - A. Information om försäkringen: En chunk per underrubrik
   - B. Regler vid köp: Håll B.1-B.10 var för sig
   - C. Allmänna begränsningar: En chunk per C-punkt
   - D. Olycksfall: Strukturerad chunkning efter definition, ersättning, etc.
   - E. Sjukdom: Samma mönster som D
   - F. Allmänna bestämmelser: F.1-F.10 var för sig

5. **Tabeller och beloppslogik**:
   - Behåller varje tabell i ett stycke (en chunk)
   - Lägger till tolkningsinformation efter tabeller

6. **Rik metadata per chunk**:
   - section_code: t.ex. D.2
   - section_title: t.ex. Medicinsk invaliditet
   - topic_tags: 3-6 nyckelord
   - page_start/page_end
   - has_table: bool
   - icd_codes: lista om avsnittet innehåller ICD
   - applies_to: olycksfall | sjukdom | båda
   - eligibility/limitations: sammanfattningsflaggor
   - effective_date: giltighetsdatum

7. **Normaliserad chunk-layout**:
   - Rubrik: D.7 Ersättning vid sjukhusvistelse
   - Gäller för: olycksfall / sjukdom / båda
   - Ersätter: ...
   - Ersätter inte: ...
   - När rätt uppstår: ...
   - Utbetalning: ...
   - Viktiga undantag/korsreferenser: ...

## Kodstruktur

Projektet är uppdelat i flera moduler för att göra koden mer lättförståelig och underhållbar:

- **pdf_chunker.py**: Huvudskriptet som hanterar kommandoradsargument och koordinerar processen
- **models.py**: Definierar datamodeller som `LegalChunk`-klassen
- **legal_chunker.py**: Implementerar chunkning-strategin för juridiska dokument
- **chunk_utils.py**: Hjälpfunktioner för chunkning och textanalys
- **metadata_extractor.py**: Funktioner för att extrahera metadata från text
- **db_handler.py**: Funktioner för att spara chunks i databasen eller JSON-filer

### Felhantering

Verktyget har robust felhantering för att hantera olika typer av fel:

- **FileNotFoundError**: Om PDF-filen inte finns
- **PermissionError**: Om PDF-filen inte kan läsas på grund av behörighetsproblem
- **ValueError**: Om ingen text kunde extraheras eller inga chunks kunde skapas
- **RuntimeError**: Om det uppstår fel vid bearbetning eller lagring

Felmeddelanden är tydliga och hjälpsamma för att underlätta felsökning.

## Integration med befintligt system

Verktyget kan integreras med det befintliga backend-systemet för att lagra chunks i databasen och generera embeddings med antingen Gemini API eller lokala modeller.

### Användning med Gemini API

För att använda Gemini API för embeddings, se till att din API-nyckel är konfigurerad i miljövariabeln `GEMINI_API` och kör:

```bash
python scripts/pdf_chunker.py backend/rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf
```

### Användning med lokala embeddings

För att använda lokala embeddings (sentence-transformers), lägg till `--local`-flaggan:

```bash
python scripts/pdf_chunker.py backend/rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf --local
```

### Programmatisk användning

Du kan också använda verktyget programmatiskt i din egen kod:

```python
from scripts.pdf_chunker import test_chunking

# Testa chunkning utan att spara resultat
chunks = test_chunking(
    pdf_path="path/to/document.pdf",
    chunk_size=300,
    min_chunk=150,
    max_chunk=400,
    overlap=50
)

# Gör något med chunks
for chunk in chunks:
    print(f"Chunk: {chunk.section_code} {chunk.section_title}")
    print(f"Content: {chunk.content[:100]}...")
```
