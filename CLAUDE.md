# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Polish Financial Statements (Sprawozdania Finansowe - SF) schema analysis and conversion project. It contains XML Schema Definition (XSD) files for financial reporting according to Polish accounting standards maintained by the Polish Ministry of Finance (Ministerstwo Finansów).

**Primary purpose:** Analyze, document, and convert financial statement schemas and data for Polish companies of different sizes.

## Directory Structure

- **Przykłady konwersji/** - Conversion examples with paired XML/XLSX files (subdirectories 0-8)
- **Przykłady sprawozdań/** - Sample financial report XML files
- **Struktury SF do obróbki/** - Official SF schemas organized by version (1.0, 1.2, 1.3)
- **Struktury SF-robocze/** - Working/experimental schemas by entity type (Mikro, Mała, Inna)
- **Słowniczek schematów SF.xlsx** - Master schema dictionary mapping field codes to descriptions

## Schema Architecture

```
Base Layer:
└── StrukturyDanychSprFin (v1-2, v1-5) - Core financial data structures

Entity Types (each has versions 1-0, 1-2, 1-3):
├── JednostkaMikro - Micro entities (simplified reporting)
├── JednostkaMala - Small entities (medium complexity)
└── JednostkaInna - Other/Large entities (comprehensive reporting)

Currency Variants:
├── WZlotych - Amounts in PLN (exact)
└── WTysiacach - Amounts in thousands
```

## Key Conventions

- All schemas use Polish naming conventions and annotations
- Schema versioning follows format `vX-Y` (e.g., v1-0, v1-2, v1-3)
- Entity type prefixes: `JednostkaMikro`, `JednostkaMala`, `JednostkaInna`
- XSD files come in pairs: structure definitions (`StrukturyDanychSprFin`) and entity reports (`JednostkaXXXWZlotych`)

## Working with this Project

This is a data structure project, not a software project. Common tasks include:
- Validating XML files against XSD schemas
- Analyzing schema differences between versions
- Converting financial data between XML and Excel formats
- Reviewing dictionary mappings in XLSX files
- Examining financial statement structure patterns

## File Types

- **XSD** (22 files) - XML Schema definitions for validation
- **XLSX** (14 files) - Dictionaries and conversion examples
- **XML** (13 files) - Sample financial statements
- **PDF** (3 files) - Reference/visualization documents
