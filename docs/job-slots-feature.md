# Industry Job Slots Overview Feature

## Overview
This feature provides a comprehensive view of industry job slot capacity and availability for all characters linked to the user's account. It helps industrialists quickly identify which characters have free capacity for new manufacturing, research, or reaction jobs.

## New Features (Enhanced Version)

### 1. **Skill Data Caching**
- Skills are cached for 3 hours to reduce ESI API calls
- Automatic cache refresh when data expires
- Significantly improves page load times on repeated visits
- Reduces load on ESI servers

### 2. **Corporation View**
- View job slots for all corporation members
- Requires `can_manage_corp_bp_requests` permission
- Toggle between personal and corporation views
- Separate summary statistics for corporation scope

### 3. **Time to Next Free Slot**
- Shows when the next slot will become available
- Displays human-readable time format (e.g., "2h 15m", "1d 3h")
- Only shown when category is at full capacity
- Helps plan job queuing strategy

### 4. **Sortable Columns**
- Click any column header to sort
- Sort by:
  - Character name (alphabetical)
  - Manufacturing slots available
  - Research slots available
  - Reactions slots available
  - Average utilization percentage
- Toggle between ascending and descending order
- Sort state preserved across page refreshes

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
   - **Scope Selector** (if you have corporation permissions):
     - "My Characters": Show only your own characters
     - "Corporation": Show all corporation members' characters
   - Summary statistics at the top
   - Detailed character breakdown in a table
   - Color-coded indicators showing utilization levels
   - Time until next slot becomes available (when fully utilized)
   - Sortable column headers - click to sort
4. Click any column header to sort the table:
   - Click once for ascending order
   - Click again for descending order
   - Sort icon shows current sort direction

## Use Cases

### Finding Available Characters
Quickly identify which characters have free slots to start new jobs without checking each one individually in-game.

### Corporation Management
View slot availability across all corporation members to optimize job distribution.

### Resource Planning
Plan job scheduling across multiple characters by seeing the complete capacity picture and when slots will become available.

### Skill Training Priority
Identify characters that would benefit most from training industry skills to increase slot capacity.

### Bottleneck Identification
Spot characters that are at or near capacity and may need job redistribution. See when their next slot becomes free.

### Quick Sorting
Sort by available slots to instantly find characters with the most capacity, or by utilization to find the busiest characters.

## Database Impact
- **Queries**: O(n) where n is the number of characters (user's or corporation)
  - One query to fetch character ownerships
  - One cache lookup per character for skills (or ESI call if cache miss/expired)
  - One query per character for active jobs (with subqueries for next free slot)
- **Database writes**: CharacterSkillsCache table (skills cached for 3 hours)
- **Caching**: 
  - Skill data cached in database for 3 hours (CharacterSkillsCache model)
  - ESI client includes retry logic and rate limiting
  - Significant performance improvement on repeat visits

## Testing
Comprehensive test suite included in `indy_hub/tests/test_job_slots.py`:
- URL resolution
- Slot calculations for all three categories
- Active job counting
- ESI error handling
- Totals calculation across multiple characters
- Edge cases (no characters, no skills, etc.)
- **NEW**: Skills caching and cache expiry
- **NEW**: Corporation scope permission checks
- **NEW**: Sorting by different columns
- **NEW**: Next free slot time calculation

## Models

### CharacterSkillsCache
New model to cache skill data:
## Security
- ✅ No SQL injection vulnerabilities
- ✅ Proper authentication and permission checks
- ✅ Only displays data for characters owned by the authenticated user (or corporation members with permission)
- ✅ Corporation view requires `can_manage_corp_bp_requests` permission
- ✅ ESI token validation enforced
- ✅ No XSS vulnerabilities (all user data properly escaped in templates)
- ✅ Skills cache stored securely in database
- ✅ CodeQL security scan passed with 0 alerts

## Implemented Enhancements

✅ **All features from the original "Future Enhancements" have been implemented:**

1. ✅ **Caching**: Skill data cached for 3 hours to reduce ESI calls
2. ✅ **Corporation View**: Show slots for corporation members (with can_manage_corp_bp_requests permission)
3. ✅ **Time to Free Slot**: Display when the next job completes to free a slot
4. ✅ **Sorting**: Allow sorting the table by available slots, character name, or utilization

## Future Enhancements

Additional possible improvements:

1. **Filtering**: Filter to show only characters with available slots
2. **Export**: Export the slot overview to CSV or JSON
3. **Notifications**: Alert when slots become available
4. **Historical Tracking**: Track slot utilization over time
5. **Mobile App Integration**: API endpoint for mobile apps

## References
- EVE Online Industry Skills: https://wiki.eveuniversity.org/Industry
- ESI Skills API: https://esi.evetech.net/ui/#/Skills
- ESI Industry API: https://esi.evetech.net/ui/#/Industry
