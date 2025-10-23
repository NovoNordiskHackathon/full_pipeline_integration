# Clinical Trial Data Processing Pipeline

A modular pipeline for processing clinical trial protocol and eCRF JSON files to generate comprehensive schedule grids and study-specific forms for clinical trial planning.

## Available Pipelines

### 1. PTD Schedule Grid Generator (`generate_ptd.py`)
Generates comprehensive schedule grids for clinical trial planning.

### 2. Study Specific Forms Generator (`Final_study_specific_form.py`)
Generates study-specific forms from eCRF JSON files with detailed item analysis and Excel formatting.

## Overview

This tool refactors and merges multiple existing scripts into a single, clean, modular pipeline that produces a `schedule_grid.csv` file. The pipeline is designed to be configurable and reusable by others.

## Features

- **Modular Design**: Each processing stage is a separate, configurable module
- **Configuration-Driven**: JSON configuration files for each module allow customization without code changes
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Intermediate File Management**: Option to keep or clean up intermediate files
- **Error Handling**: Robust error handling with informative messages

## PTD Schedule Grid Pipeline Stages

1. **Form Extraction** (`extract_forms`): Extract form information from eCRF JSON
2. **SoA Parsing** (`parse_soa`): Parse schedule of activities from protocol JSON
3. **Common Matrix** (`merge_common_matrix`): Create ordered SoA matrix with fuzzy matching
4. **Event Grouping** (`group_events`): Generate visit groups with event windows
5. **Schedule Layout** (`generate_schedule_grid`): Create final schedule grid layout

## Study Specific Forms Pipeline

The Study Specific Forms Generator processes eCRF JSON files to extract detailed form information and generate comprehensive Excel reports with:

- **Form Analysis**: Extracts form labels, names, and hierarchical structure
- **Item Extraction**: Identifies and processes form items with proper validation
- **Data Type Detection**: Automatically determines data types (Text, Codelist, Date/Time, etc.)
- **Item Grouping**: Analyzes repeating and non-repeating item groups
- **Validation Rules**: Applies business rules for required fields, codelists, and data validation
- **Excel Output**: Generates formatted Excel files with proper structure and styling

## Installation

No additional dependencies beyond the existing project requirements. The pipeline uses the same libraries as the original scripts.

## Usage

### PTD (Schedule Grid + Study Specific Forms)

```bash
python generate_ptd.py \
  --protocol hierarchical_output_final_protocol.json \
  --ecrf hierarchical_output_final_ecrf.json \
  --out ./output/ptd.xlsx
```

## Study Specific Forms Generator Usage (standalone)

```bash
python Final_study_specific_form.py hierarchical_output_final_ecrf.json
```

This creates `Study_Specific_Form.xlsx` in the current directory.

### Command Line Options

- `--protocol`: Path to protocol JSON file (required)
- `--ecrf`: Path to eCRF JSON file (required)
- `--out`: Final output Excel path (e.g., `./output/ptd.xlsx`) (required)

## Study Specific Forms Excel Layout

The exported Study Specific Forms sheet uses a clean, three-row header with grouped subheaders and data starting on row 4:

- **Row 1 (CTDM)**: Only columns A–D are populated once with:
  - `CTDM to fill in`
  - `CTDM Optional, if blank CDP to propose`
  - `Input needed from SDTM`
  - `CDAI input needed`
  Columns E+ are left blank and unstyled.

- **Row 2 (Group Headers)**: Each group name is a single merged cell spanning the width of its subheaders in Row 3. Centered text with a light background color.

- **Row 3 (Subheaders)**: Individual cells (no merging), filled with the corresponding group color.

- **Row 4+ (Data)**: Item rows begin at row 4.

Group order and subheader counts:

1. **Source** (1)
   - New or Copied from Study
2. **Form** (2)
   - Form Label; Form Name (provided by SDTM Programmer, if SDTM linked form)
3. **Item Group** (5)
   - Item Group (if only one on form, recommend same as Form Label)
   - Item group Repeating
   - Repeat Maximum, if known, else default =50
   - Display format of repeating item group (Grid, read only, form)
   - Default Data in repeating item group
4. **Item** (3)
   - Item Order; Item Label; Item Name (provided by SDTM Programmer, if SDTM linked item)
5. **Progressive Display** (3)
   - Progressively displayed?; Controlling item (item triggering it, if yes, describe item below); Controlling item value
6. **Data Type** (3)
   - Data type; If text or number, Field Length; If number, Precision (decimal places)
7. **Codelist** (4)
   - Codelist – Choice Labels (if binary, can use Goodlist Table); Codelist Name (provided by SDTM Programmer); Choice Code (provided by SDTM Programmer); Codelist Control Type
8. **System Queries** (4)
   - If number, Range: Min Value / Max Value; Date: Query Future Date; Required; If Required, Open Query when intentionally left blank (form/item)
9. **Notes** (1)
   - Notes

Notes:
- Only Row 2 uses merged cells. Rows 1 and 3 have no merged cells.
- Group colors are light pastels for readability; column widths are auto-adjusted.
- In the combined PTD, the forms sheet is copied with merged regions preserved and header colors retained.

## Configuration

Each module has its own JSON configuration file in the `config/` directory:

### config_form_extractor.json
Configures form extraction from eCRF JSON:
- Input/output paths
- Visit patterns and trigger patterns
- Source classification rules
- Form name validation patterns

### config_soa_parser.json
Configures schedule of activities parsing:
- Visit patterns and cell markers
- Header keywords and section breaks
- Procedure filtering rules
- Table detection parameters

### config_common_matrix.json
Configures the SoA matrix generation:
- Fuzzy matching threshold
- Column mappings
- Visit parsing options
- Output column configuration

### config_event_grouping.json
Configures event grouping and visit windows:
- Visit normalization patterns
- Event group definitions
- Extension detection rules
- Visit window calculations

### config_schedule_layout.json
Configures the final schedule grid layout:
- Column mappings
- Event name patterns
- Triggering rules
- Styling options

## Output Files

### Final Output
- `ptd.xlsx` (or the value passed to `--out`): Contains two sheets:
  - `Schedule Grid`: The schedule grid
  - `Study Specific Forms`: The study-specific forms with the 3-row header layout described above

### Intermediate Files
- `extracted_forms.csv`: Forms extracted from eCRF JSON (temporary)
- `schedule.csv`: Schedule of activities parsed from protocol JSON (temporary)
- `soa_matrix.csv`: Ordered SoA matrix with fuzzy matching (temporary)
- `visits_with_groups.xlsx`: Visit groups with event windows (temporary)

## Module Structure

```
modules/
├── __init__.py
├── form_extractor.py      # Extract forms from eCRF JSON
├── soa_parser.py          # Parse schedule of activities
├── common_matrix.py       # Create ordered SoA matrix
├── event_grouping.py      # Group events and create visit windows
└── schedule_layout.py     # Generate final schedule grid
```

## Configuration Examples

### Example: Custom Visit Patterns

```json
{
  "visit_patterns": [
    "\\bV\\d+[A-Za-z]*\\b",
    "\\bP\\d+[A-Za-z]*\\b",
    "\\bS\\d+D[\\s-]?\\d+[A-Za-z]*\\b"
  ]
}
```

### Example: Custom Fuzzy Matching Threshold

```json
{
  "fuzzy_threshold": 0.7,
  "include_unmapped": true
}
```

### Example: Custom Event Groups

```json
{
  "event_groups": {
    "screening": {
      "visit_names": ["V1"],
      "group_name": "Screening"
    },
    "randomisation": {
      "visit_names": ["V2"],
      "group_name": "Randomisation"
    }
  }
}
```

## Error Handling

The pipeline includes comprehensive error handling:
- File not found errors
- JSON parsing errors
- Configuration validation
- Data processing errors
- Graceful cleanup on failure

## Logging

The pipeline provides detailed logging:
- Progress through each stage
- Configuration loading
- File processing statistics
- Error messages and stack traces
- Performance metrics

Logs are written to both console and `ptd_generation.log` file.

## Migration from Original Scripts

This pipeline replaces the following original scripts:
- `form_label_form_name_extractor.py` → `modules/form_extractor.py`
- `soa_works_for_all.py` → `modules/soa_parser.py`
- `extracting_commonform_visits.py` → `modules/common_matrix.py`
- `event_grouping_and_event_window_configuration.py` → `modules/event_grouping.py`
- `schedule_grid_final_layout.py` → `modules/schedule_layout.py`
- `main_integration.py` → `generate_ptd.py`

## Troubleshooting

### Common Issues

1. **Configuration file not found**: Ensure config files are in the `config/` directory
2. **JSON parsing errors**: Verify input JSON files are valid
3. **Missing columns**: Check that input files have expected column names
4. **Permission errors**: Ensure write permissions for output directory

### Debug Mode

Use `--log-level DEBUG` to get detailed information about the processing steps.

### Keeping Intermediate Files

Use `--keep-intermediates` to examine intermediate files for debugging.

## Contributing

When modifying the pipeline:
1. Update the relevant module in `modules/`
2. Update the corresponding configuration file in `config/`
3. Test with both existing and new data
4. Update documentation as needed

## License

Same as the original project.
