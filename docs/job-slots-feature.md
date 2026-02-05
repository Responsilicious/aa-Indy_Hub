# Industry Job Slots Overview Feature

## Overview
This feature provides a comprehensive view of industry job slot capacity and availability for all characters linked to the user's account. It helps industrialists quickly identify which characters have free capacity for new manufacturing, research, or reaction jobs.

## Features

### Slot Calculation
The system calculates available slots based on trained skills:

#### Manufacturing Slots
- **Base**: 1 slot (always available)
- **Mass Production** (Skill ID: 3387): +1 slot per level
- **Advanced Mass Production** (Skill ID: 24625): +1 slot per level
- **Maximum**: 11 slots (1 base + 5 + 5)

#### Research Slots
- **Base**: 1 slot (always available)
- **Laboratory Operation** (Skill ID: 3406): +1 slot per level
- **Advanced Laboratory Operation** (Skill ID: 24624): +1 slot per level
- **Maximum**: 11 slots (1 base + 5 + 5)

#### Reactions Slots
- **Base**: 1 slot (only if Mass Reactions is trained)
- **Mass Reactions** (Skill ID: 45748): +1 slot per level (minimum level 1 required)
- **Advanced Mass Reactions** (Skill ID: 45749): +1 slot per level
- **Maximum**: 11 slots (1 base + 5 + 5)
- **Minimum**: 0 slots (if Mass Reactions not trained)

### Job Activity Mapping

The feature categorizes active jobs into three types:

1. **Manufacturing**: Activity ID 1
2. **Research**: Activity IDs 3 (TE Research), 4 (ME Research), 5 (Copying), 8 (Invention)
3. **Reactions**: Activity ID 9

### Display Features

#### Summary Statistics
- Total number of linked characters
- Aggregate available/total slots across all characters for each category
- Color-coded availability indicators

#### Character Details Table
For each character, the view displays:
- Character portrait and name
- Manufacturing: Available / Total slots with utilization bar
- Research: Available / Total slots with utilization bar
- Reactions: Available / Total slots with utilization bar (or "No reaction slots" if not trained)

#### Visual Indicators
- 🟢 **Green** (< 50% utilization): Good availability
- 🟡 **Yellow** (50-90% utilization): Limited availability
- 🔴 **Red** (> 90% utilization): Low availability

### Technical Implementation

#### Required ESI Scopes
- `esi-skills.read_skills.v1` - Read character skills
- `esi-industry.read_character_jobs.v1` - Read character industry jobs
- `esi-universe.read_structures.v1` - Read structure information

#### URL Route
- Path: `/indy_hub/job-slots/`
- View: `industry_job_slots`
- Name: `industry_job_slots`

#### Access Control
- Requires user authentication
- Requires `can_access_indy_hub` permission
- Requires valid ESI tokens with the necessary scopes

#### Error Handling
- Gracefully handles ESI API errors
- Falls back to base slots (1 for manufacturing, 1 for research, 0 for reactions) if skills cannot be fetched
- Logs warnings for failed skill fetches while continuing with remaining characters

## Usage

1. Navigate to the main Indy Hub dashboard
2. In the Industry section, click the **Slots** button
3. The view displays:
   - Summary statistics at the top
   - Detailed character breakdown in a table
   - Color-coded indicators showing utilization levels
   - Legend explaining the color codes

## Use Cases

### Finding Available Characters
Quickly identify which characters have free slots to start new jobs without checking each one individually in-game.

### Resource Planning
Plan job scheduling across multiple characters by seeing the complete capacity picture.

### Skill Training Priority
Identify characters that would benefit most from training industry skills to increase slot capacity.

### Bottleneck Identification
Spot characters that are at or near capacity and may need job redistribution.

## Database Impact
- **Queries**: O(n) where n is the number of user characters
  - One query to fetch character ownerships
  - One ESI call per character for skills
  - One query per character for active jobs
- **No database writes**: This is a read-only view
- **Caching**: ESI client includes retry logic and rate limiting

## Testing
Comprehensive test suite included in `indy_hub/tests/test_job_slots.py`:
- URL resolution
- Slot calculations for all three categories
- Active job counting
- ESI error handling
- Totals calculation across multiple characters
- Edge cases (no characters, no skills, etc.)

## Security
- ✅ No SQL injection vulnerabilities
- ✅ Proper authentication and permission checks
- ✅ Only displays data for characters owned by the authenticated user
- ✅ ESI token validation enforced
- ✅ No XSS vulnerabilities (all user data properly escaped in templates)
- ✅ CodeQL security scan passed with 0 alerts

## Future Enhancements (Not Implemented)

Possible future improvements could include:

1. **Caching**: Cache skill data for a few hours to reduce ESI calls
2. **Corporation View**: Show slots for corporation members (with appropriate permissions)
3. **Time to Free Slot**: Display when the next job completes to free a slot
4. **Sorting**: Allow sorting the table by available slots, character name, or utilization
5. **Filtering**: Filter to show only characters with available slots
6. **Export**: Export the slot overview to CSV or JSON
7. **Notifications**: Alert when slots become available
8. **Historical Tracking**: Track slot utilization over time

## References
- EVE Online Industry Skills: https://wiki.eveuniversity.org/Industry
- ESI Skills API: https://esi.evetech.net/ui/#/Skills
- ESI Industry API: https://esi.evetech.net/ui/#/Industry
