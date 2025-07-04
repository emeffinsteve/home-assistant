# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Home Assistant Configuration Management

This is a Home Assistant configuration using the **packages system** for modular organization. Configuration is split across several key areas rather than having everything in one large configuration.yaml file.

### Key Commands

**Configuration Management:**
- Check configuration: `ha core check`
- Restart Home Assistant: `ha core restart`  
- Reload specific components: `ha core reload --type automation`
- Reload templates: `ha core reload --type template`
- Reload scripts: `ha core reload --type script`

**Package Development:**
- Add new functionality in `/config/packages/` as self-contained YAML files
- Use Developer Tools → Template to test Jinja2 expressions
- Test automations with Developer Tools → Services

### Architecture Overview

**Package-Based Organization:**
- Primary configuration logic lives in `/config/packages/` directory
- Each package file is self-contained with its own entities, automations, and scripts
- Current packages: `climate_management.yaml`, `internet_management.yaml`, `signal_kids.yaml`

**Configuration Structure:**
- `/config/configuration.yaml` - Main config with light groups and includes
- `/config/packages/` - Modular functionality packages  
- `/config/power_sensors.yaml` - Template-based power consumption calculations
- `/config/energy_sensors.yaml` - Integration sensors for energy tracking
- `/config/all_templates.yaml` - Template aggregation

**Custom Components:**
- **Dreo**: Smart device integration (fans, heaters, humidifiers)
- **Eero**: Network management and parental controls
- **HACS**: Community store for custom integrations
- **Govee**: Smart lighting with learning capabilities

### Error Handling & Debugging

**Resilience Patterns:**
- Multiple sensor fallbacks (outdoor sensor → weather service → indoor-only)
- Coordination locks prevent automation conflicts
- `persistent_notification.create` for user-visible errors
- `system_log.write` for component-level logging

**Common Issues:**
- Custom components may need restart after updates
- Template syntax errors break entire template files
- Package includes require specific YAML structure
- HACS components update through UI, not files

### Frontend Customization

**HACS-Managed Resources:**
- Custom cards in `/config/www/community/`
- Themes in `/config/themes/bubble/`
- Frontend modules loaded via `extra_module_url`

**Key Integrations:**
- Bubble Card for modern dashboard UI
- Card-mod for advanced styling
- Mushroom cards for compact layouts

### CUSTOM INSTRUCTIONS:
PROJECT INSTRUCTIONS: Home Assistant Automation Project
VERSION: 2.2.0 (Major.Minor.Patch)
CREATED: 2025-06-24
LAST UPDATED: 2025-06-28
DEPENDENCIES: Home Assistant, Developer Tools, logbook integration

CHANGELOG:
- v2.2.0 - 2025-06-28 - Major: Merged testing and debugging protocols, eliminated conflicts, unified standards
- v2.1.1 - 2025-06-28 - Updated comprehensive testing verification with script-based testing and UI instructions
- v2.1.0 - 2025-06-28 - Added enhanced headers, automated log analysis, comprehensive testing, package sharing standards
- v2.0.0 - 2025-06-28 - Added enhanced validation, Claude self-review, backup procedures, secrets management
- v1.1.0 - 2025-06-24 - Added debugging protocols, Jinja2 best practices, template testing
- v1.0.0 - 2025-06-24 - Initial project standards and requirements

DESCRIPTION: Complete standards for HA automation development and debugging

PROJECT OVERVIEW
All work in this project is exclusively for Home Assistant automations. Every automation must follow these standards without exception, regardless of chat session or complexity.

CLAUDE SELF-REVIEW MANDATE
Before presenting any YAML code, Claude must perform systematic self-review:
1. Verify all entity references exist and are correctly formatted
2. Check template syntax using HA Jinja2 standards
3. Validate YAML structure and indentation (2-space, no tabs)
4. Confirm all dependencies are listed in header
5. Ensure logging requirements are met
6. Test complex templates in conceptual isolation
7. Verify backup creation instructions are included
8. Acknowledge uncertainty with "I may be hallucinating" rather than making excuses

MULTI-FILE CONFLICT ANALYSIS
When working on new packages or scripts, analyze these files for conflicts:
packages/*.yaml, scripts.yaml, scenes.yaml, energy_sensors.yaml, configuration.yaml, automations.yaml, all_templates.yaml

Create master entity usage map showing:
Which automations control which entities
Timing and trigger patterns
Potential conflicts requiring human review

Flag potential conflicts but acknowledge human judgment required for:
Intentional coordination between automations
Timing-based conflicts
Priority and override scenarios
Conditional logic interactions

AUTOMATED LOG ANALYSIS WORKFLOW
When user requests log analysis, offer three options:
1. Automation/Template Issues: tail -200 /config/home-assistant.log | grep -i "automation\|template\|error" > /config/recent-logs.txt
2. Integration/Component Problems: tail -100 /config/home-assistant.log | grep -i "integration\|component\|failed" > /config/recent-logs.txt
3. All Recent Activity: tail -100 /config/home-assistant.log > /config/recent-logs.txt

User can also request specific searches like:
"look for the last 150 errors" → tail -150 /config/home-assistant.log | grep -i "error\|failed\|exception" > /config/recent-logs.txt
"check logs for entity problems" → grep -i "entity\|unavailable" /config/home-assistant.log | tail -50 > /config/recent-logs.txt

Always execute this workflow:
1. Clear previous file: > /config/recent-logs.txt
2. Execute appropriate log command
3. Analyze /config/recent-logs.txt for issues
4. Report findings with specific fixes
5. Clean up: > /config/recent-logs.txt

Accept natural language requests and translate to appropriate log commands.

ENHANCED BACKUP AND ROLLBACK PROCEDURES
Before any file modifications:
Create timestamped backup: cp filename filename.backup.$(date +%Y%m%d_%H%M)
Standard rollback process:
1. cp filename.backup filename
2. ha core check
3. ha core reload --type automation
4. Verify functionality through templates or entity states
5. If rollback fails, try previous backup version

Multiple backup management:
Keep last 5 backups: find /config -name "*.backup.*" -type f | sort -r | tail -n +6 | xargs rm -f

PRE-DEPLOYMENT VALIDATION CHECKLIST
Before every deployment, run these commands in order:

Enhanced YAML Validation:
python3 -c "
import yaml, sys
try:
    with open('[filename]') as f:
        data = yaml.safe_load(f)
    print('✓ Valid YAML syntax')
    if isinstance(data, dict):
        for key in data.keys():
            if key.startswith(' ') or key.endswith(' '):
                print(f'⚠ Whitespace in key: {repr(key)}')
except Exception as e:
    print(f'✗ YAML Error: {e}')
"

HA Configuration Check:
ha core check

Entity Reference Validation:
grep -n "entity_id:" [filename] | grep -v "#"
grep -n "states(" [filename] | grep -v "#"

Template Syntax Check:
grep -n "{{" [filename] | head -10
grep -n "{%" [filename] | head -10

Secrets Management Check:
grep -n "api_key\|password\|token" [filename] | grep -v "!secret"

UNIFIED TESTING AND DEBUGGING PROTOCOLS

Template Development Standards
MANDATORY: All complex templates must be tested in Developer Tools → Template before implementation.

Template Development Process:
1. Test individual entity states: {{ states('entity.name') }}
2. Test availability checks: {{ is_state('entity.name', 'unavailable') }}
3. Build incrementally - add one component at a time
4. Test complete template logic in isolation
5. Verify expected vs actual output

ALWAYS use HA's filter-based approaches over complex loops:

Preferred (Filter-based):
available_entities: "{{ light_entities | reject('is_state', 'unavailable') | list }}"
original_states: "{{ dict.from_keys(available_entities, states) }}"
entity_count: "{{ light_entities | length }}"
entity_names: "{{ available_entities | join(', ') }}"

Avoid (Loop-based patterns with scoping issues):
available_entities: >-
  {% set available = [] %}
  {% for entity in light_entities %}
    {% set available = available + [entity] %}
  {% endfor %}
  {{ available }}

Filter Methods vs Complex Logic:
Use | select(), | reject(), | map(), | list over manual loops
Use | default() over conditional checks where possible
Leverage HA's built-in template functions: states(), state_attr(), is_state()

Template Reliability Standards:
Entity Availability Detection:
available_entities: "{{ light_entities | reject('is_state', 'unavailable') | list }}"

State Capture and Restoration:
original_states: >-
  {% set states_dict = {} %}
  {% for entity in available_entities %}
    {% set states_dict = dict(states_dict, **{entity: states(entity)}) %}
  {% endfor %}
  {{ states_dict }}

original_state: "{{ original_states[entity] }}"

Safe Defaults and Error Handling:
current_brightness: "{{ state_attr(entity, 'brightness') or 128 }}"
entity_count: "{{ available_entities | length | default(0) }}"

Entity Validation in Automations:
condition:
  - condition: template
    value_template: "{{ states('light.living_room') != 'unavailable' }}"

Performance Guidelines and Warnings
Performance Warning Triggers:
- Templates with 4+ nested filters
- Loops processing 15+ items
- Templates with calculation delays over 2 seconds (excludes intentional timing)
- Variable lists over 100 items (variables persist until HA restart)
- Sensor update frequency above once per minute

When Claude detects performance concerns:
1. Present the code with warnings clearly marked
2. Explain the performance implications
3. Request explicit approval before proceeding
4. Offer alternative approaches if available
5. DO NOT write files without user approval when warnings are present

Warning Format:
"⚠️ PERFORMANCE WARNING: This template uses 4+ nested filters and processes 15+ items
Potential impact: Slower execution, increased resource usage
Alternatives: [suggest simpler approaches]
Proceed with implementation? (y/n)"

Primary Testing Method: Script-Based Testing with Logging
Create test scripts with comprehensive logging for automated verification:

# Add to scripts.yaml or scripts section
test_[automation_name]:
  alias: "Test [Automation Name]"
  sequence:
    - action: logbook.log
      data:
        name: "TEST_[AUTOMATION_NAME]"
        message: "START: Beginning test sequence"
        domain: "script"
    
    - action: input_boolean.turn_off
      target:
        entity_id:
          - [reset_entities_here]
    
    - action: logbook.log
      data:
        name: "TEST_[AUTOMATION_NAME]"
        message: "RESET: Entities reset - [entity1]: {{ states('[entity1]') }}, [entity2]: {{ states('[entity2]') }}"
        domain: "script"
    
    - action: homeassistant.sleep
      data:
        seconds: 2
    
    - action: automation.trigger
      target:
        entity_id: automation.[automation_name]
    
    - action: logbook.log
      data:
        name: "TEST_[AUTOMATION_NAME]"
        message: "TRIGGER: Automation triggered"
        domain: "script"
    
    - action: homeassistant.sleep
      data:
        seconds: 5
    
    - action: logbook.log
      data:
        name: "TEST_[AUTOMATION_NAME]"
        message: "STATE_CHECK: Critical states - [key_entity]: {{ states('[key_entity]') }}"
        domain: "script"
    
    - action: [completion_action]
      target:
        entity_id: [completion_entity]
    
    - action: logbook.log
      data:
        name: "TEST_[AUTOMATION_NAME]"
        message: "SUCCESS: Test complete - Final states: [entity1]={{ states('[entity1]') }}, [entity2]={{ states('[entity2]') }}"
        domain: "script"

UI-Based Test Execution:
1. Go to Developer Tools → Actions
2. In Action field, type: script.turn_on
3. In Target section, Entity ID field, type: script.test_[automation_name]
4. Click "Perform Action"
5. Wait for completion (watch for script.test_[automation_name] to change from "on" to "off")
6. Proceed to log analysis

Automated Log Analysis:
# Clear previous results
> /config/test_results.txt

# Extract test logs from last 100 lines
tail -100 /config/home-assistant.log | grep -i "TEST_[AUTOMATION_NAME]" > /config/test_results.txt

# Display results
cat /config/test_results.txt

Real-Time Template Verification:
Use this master template in Developer Tools → Template for real-time state monitoring:

# Test Verification Template - Copy/paste into Developer Tools → Template
Test Status for [AUTOMATION_NAME]:

=== ENTITY STATES ===
{% set test_entities = ['[entity1]', '[entity2]', '[entity3]'] %}
{% for entity in test_entities %}
- {{ entity }}: {{ states(entity) }}{% if states(entity) == 'unavailable' %} ⚠️ UNAVAILABLE{% endif %}
{% endfor %}

=== AVAILABILITY CHECK ===
Available Entities: {{ test_entities | reject('is_state', 'unavailable') | list | length }}/{{ test_entities | length }}
{% set unavailable = test_entities | select('is_state', 'unavailable') | list %}
{% if unavailable %}
⚠️ Unavailable: {{ unavailable | join(', ') }}
{% endif %}

=== AUTOMATION STATUS ===
Automation State: {{ states('automation.[automation_name]') }}
Last Triggered: {{ state_attr('automation.[automation_name]', 'last_triggered') }}

=== TEST EXECUTION STATUS ===
Test Script State: {{ states('script.test_[automation_name]') }}
{% if states('script.test_[automation_name]') == 'on' %}
🔄 TEST RUNNING
{% else %}
✅ TEST READY/COMPLETE
{% endif %}

=== CRITICAL CONDITIONS ===
[Add specific conditions to verify, e.g.:]
- Expected State A: {{ 'PASS' if is_state('[entity1]', '[expected_state]') else 'FAIL' }}
- Expected State B: {{ 'PASS' if is_state('[entity2]', '[expected_state]') else 'FAIL' }}

=== TIMESTAMP ===
Checked at: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}

CLI Analysis Integration:
"Analyze the test results in /config/test_results.txt and determine:
1. Did all logged steps execute in the correct sequence?
2. Were the expected state changes achieved based on the STATE_CHECK entries?
3. Did any errors occur during execution?
4. Does the SUCCESS entry show the expected final states?
5. Generate a PASS/FAIL determination with specific reasons
6. If FAIL, suggest specific debugging steps"

Systematic Debugging Process
Never exceed 2-3 failures before systematic debugging:
1. First failure: Review template syntax and logic
2. Second failure: Test template components in Developer Tools
3. Third failure: Break down into individual components and test each

When templates fail repeatedly:
1. Isolate the failing component - test each template piece separately
2. Use Developer Tools extensively - validate every assumption
3. Choose simpler approaches - filters over loops, built-ins over custom logic
4. Document what was tested - avoid repeating failed approaches

Integration Testing Requirements:
- Verify dependent automations still function correctly
- Test edge cases with unavailable entities
- Confirm automation triggers at expected times
- Monitor template output for state changes during testing
- Copy automation traces to CLI for detailed execution review
- Verify all conditions and actions executed as expected

User Acceptance Testing:
- Confirm automation solves original problem
- Test manual overrides work correctly
- Verify error handling and fallback behaviors
- Ensure notifications and logging work as expected

SECRETS MANAGEMENT
MANDATORY: All sensitive data must use secrets.yaml:
Configuration reference: api_key: !secret weather_api_key
Secrets file entry: weather_api_key: your_actual_key_here
This prevents accidental sharing when distributing automation packages
Never use plain-text secrets in any configuration files
Access pattern in automations: service_data: api_key: !secret my_api_key
Keep secrets.yaml out of any shared or backup files

PACKAGE SHARING STANDARDS
When sharing automation packages:

Include:
Automation YAML with sanitized entity names
Required helper configurations
Documentation with setup instructions
Example configurations and use cases
List of required integrations
Compatibility notes (HA version requirements)

Exclude:
secrets.yaml or any plain-text credentials
Device-specific entity IDs
Personal location names or identifiers
Custom device configurations

Sanitization Process:
Replace personal entity names with generic examples
light.master_bedroom → light.example_bedroom
sensor.outdoor_temp_front_yard → sensor.outdoor_temperature
Remove location-specific coordinates or addresses
Replace personal notification targets with examples

Documentation Requirements:
README with installation steps
Required integrations list
Configuration variables to customize
Troubleshooting common issues
Changelog and version history

CLAUDE LIMITATIONS AND HALLUCINATION RISKS
Claude frequently hallucinates in these areas:
Entity existence: Often assumes entities exist without verification
HA integration capabilities: May suggest non-existent features
Complex template syntax: Jinja2 templates often contain subtle errors
Automation timing logic: May miss edge cases or race conditions
When uncertain about mistakes, acknowledge "I may be hallucinating" rather than creating explanations

GROUNDING REQUIREMENTS
Always specify HA version when suggesting features
Never suggest integration features without explicit verification
Default to basic, well-established HA features over cutting-edge ones
When uncertain about capabilities, state "verify this feature exists in your HA version"
Provide official documentation references for any advanced features

MASTER TEMPLATE STANDARDS

Enhanced Automation Header Format
Every automation must include this exact header format (65 character width):

# =================================================================
# AUTOMATION: [Descriptive Name Without Version]
# VERSION: X.X.X (Major.Minor.Patch)
# CREATED: YYYY-MM-DD
# LAST UPDATED: YYYY-MM-DD
# AUTHOR: Steve Taylor
# TESTED_ON: HA Version [specify actual version like 2025.6.0]
# DEPENDENCIES: [Required integrations, helpers, devices]
# 
# CHANGELOG:
# v1.2.1 - 2025-06-28 - Fixed: Template timeout issue with unavailable sensors
# v1.2.0 - 2025-06-25 - Added: Manual override capability, Enhanced: Error logging
# v1.1.0 - 2025-06-20 - Added: Fallback behavior for offline devices
# 
# DESCRIPTION: [Brief description of automation purpose]
# FAILURE MODE: [Continue/Halt/Fallback - what happens on failure]
# =================================================================

HEADER COMPLETION REQUIREMENTS:
Always populate these fields with actual values, never leave placeholders:
AUTHOR: Steve Taylor (always use this exact name)
TESTED_ON: Use `ha core info` to get actual HA version and populate this field

Auto-populate version detection:
Before creating headers, run: ha core info
Extract version from output and use in TESTED_ON field

Package File Strategy
For complex automation systems (3+ related automations), ALWAYS recommend creating a single package file in /homeassistant/packages/[system_name].yaml instead of individual automations. This provides:
Single file maintenance and version control
Preserved comments and headers (won't be lost to UI editor)
Logical component grouping with clear relationships
Atomic backup/restore of entire system
Master version header for complete system

NAMING AND VERSION CONTROL

Naming Convention
Format: [Category] [Location] [Function] (spaces, no version number)
Categories: Climate, Lighting, Security, Media, Notification, Utility
Examples: Climate Living Room Auto Control, Lighting Kitchen Motion Detection, Security Front Door Lock Monitor

Version Control Standards
Semantic Versioning: Major.Minor.Patch (1.2.3)
Major: Breaking changes requiring manual intervention
Minor: New features, no breaking changes
Patch: Bug fixes and small tweaks
Version only in header, never in automation name

CRITICAL DATETIME HANDLING
Home Assistant templates frequently cause timezone errors. NEVER mix offset-aware and offset-naive datetimes.

FORBIDDEN DateTime Patterns:
{{ now() - strptime(some_date, '%Y-%m-%d %H:%M:%S') }}
{{ now() - some_input_datetime }}
Any direct datetime subtraction without timezone handling

REQUIRED DateTime Patterns:
{{ now().timestamp() - (some_date | as_timestamp) }}
{{ (some_date | as_datetime | as_timestamp) }}
{{ now().replace(tzinfo=None) - some_naive_datetime }}
{{ (now().astimezone() - some_date.astimezone()).total_seconds() }}

Always use as_timestamp methodology for datetime comparisons to eliminate timezone issues entirely.

UNIFIED LOGGING AND NOTIFICATION STANDARDS

Mobile Notification Requirements:
REQUIRED notification format:
- action: notify.mobile_app_device_name
  data:
    message: "Your message content"
    title: "Notification Title"

ERROR HANDLING for notifications:
Always wrap notifications in continue_on_error for resilience:
- action: notify.mobile_app_steves_phone
  continue_on_error: true
  data:
    message: "Climate system adjusted temperature"
    title: "Home Automation Alert"

NOTIFICATION RELIABILITY best practices:
Use multiple notification targets with fallback:
- action: notify.mobile_app_steves_phone
  continue_on_error: true
  data:
    message: "{{ message_content }}"
    title: "{{ notification_title }}"
- action: persistent_notification.create
  continue_on_error: true
  data:
    title: "{{ notification_title }}"
    message: "{{ message_content }}"
    notification_id: "automation_{{ automation_name }}"

PERFORMANCE considerations:
Avoid notification spam with rate limiting:
condition:
  - condition: template
    value_template: >
      {{ (now() - state_attr('automation.this', 'last_triggered') | as_datetime).total_seconds() > 300 }}

NOTIFICATION DATA validation:
Always validate variables before sending:
- condition: template
  value_template: "{{ message_content is defined and message_content != '' }}"

Unified Logging Standards:
Every automation must log using these standardized formats (use action: logbook.log):

Log message templates:
[AUTOMATION_NAME] - START: [trigger description and values]
[AUTOMATION_NAME] - CONDITION: [condition check result and values]
[AUTOMATION_NAME] - DECISION: [what decision was made and why]
[AUTOMATION_NAME] - SUCCESS: [completed action with details]
[AUTOMATION_NAME] - ERROR: [what failed and fallback action taken]
[AUTOMATION_NAME] - OVERRIDE: [manual override detected with details]
[AUTOMATION_NAME] - STATE: [current state/mode change]

Logging Requirements:
Log every major decision point for trace analysis
Log all errors and failures to both traces and system logs
Include variable values and states in log messages
Use descriptive aliases for all action blocks
Ensure sufficient detail for remote troubleshooting via trace paste
Always include both message AND title fields in mobile notifications to prevent Firebase errors

ERROR HANDLING AND FAILURE MODES
Every automation must specify and implement:
Failure Mode: Continue/Halt/Fallback behavior
Error logging with specific failure reasons
Fallback actions when primary methods fail
Dependency checks with appropriate responses
Persistent notifications for critical failures

CHANGE IMPACT ANALYSIS
Before implementing changes, Claude must warn about:
Potential conflicts with existing automations
Dependencies that might be affected
Entities that will experience behavior changes
Required testing procedures after deployment
Estimated impact scope (low/medium/high)

ARTIFACT AND CODE VERSION CONTROL

Code Block Integrity Issues
CRITICAL: Artifact system corrupts YAML indentation when copied.

Prevention Strategies:
1. Use "Copy" button in artifact header when available
2. Manual indentation fix after pasting:
   Find: ^([a-z_]+:)$ Replace: $1 (2 spaces)
   Find: ^(name:|icon:|alias:|description:|mode:|sequence:)$ Replace: $1 (4 spaces)
3. Always verify YAML structure before saving
4. Test reload immediately after saving package files

Verification Checklist:
All input_boolean entries properly indented (2 spaces)
All name: and icon: entries properly indented (4 spaces)
All script sections properly indented (2 spaces for script names)
No "duplicated mapping key" errors on save

OVERRIDE STANDARDIZATION
When manual overrides are needed:
Helper Naming: input_boolean.[automation_name_snake_case]_override, input_datetime.[automation_name_snake_case]_override_until
Consistent override detection and logging
Standardized dashboard controls

HOME ASSISTANT YAML STYLE GUIDE COMPLIANCE
Strictly follow HA YAML requirements:
2-space indentation (no tabs)
Boolean values: true/false (lowercase only)
No truthy values: No y/n, yes/no, on/off
Comments: # Capitalized comment above line at matching indent
No trailing spaces
Consistent quote usage (avoid unless necessary)
Proper list formatting with - at same indent level
YAML 1.2 specification compliance

HARDWARE ENHANCEMENT PHILOSOPHY
Always suggest better solutions when:
Current hardware lacks necessary entities/data
Additional sensors would improve automation robustness
More reliable local-control devices are available
Provide both: ideal solution + current hardware workaround
Consider cost: Acknowledge budget constraints while suggesting upgrades

COMPLEX SYSTEM ARCHITECTURE
For multi-automation systems (climate control, internet management, security systems):
ALWAYS recommend package file approach
Separate concerns into focused automations (30-60 lines each)
Create coordination helpers to prevent conflicts
Implement priority/override systems
Design for individual component disable capability
Maintain system-wide version control

DEPENDENCY MANAGEMENT
Track all dependencies in automation headers
Log warnings when dependent automations are disabled
Create monitoring for critical automation dependencies
Document interaction patterns between related automations

DOCUMENTATION REQUIREMENTS
Master spreadsheet tracking (if requested)
Consistent formatting across all automations
Update naming if existing automations do not match standards
Maintain changelog with meaningful descriptions

IMPLEMENTATION NOTES
Mac Studio hosting: Sufficient power for verbose logging
Internet-dependent devices: 90%+ of current hardware requires internet
Log retention: HA handles automatically, no storage concerns
Version control: Comments preserved in file-based editing, stripped in UI editor

CONTEXT WINDOW OPTIMIZATION
Do not write YAML code unless explicitly requested
Maximize suggestions and actions per response
Use plain text format to minimize token usage
Prioritize dense, actionable information over formatting

CRITICAL SUCCESS FACTORS
These standards apply to every automation written in this project, regardless of chat session. Consistency is mandatory for maintainability and troubleshooting effectiveness.

Key Performance Indicators:
No more than 2-3 iterations due to technical failures
All templates tested in Developer Tools before implementation
Use of HA-preferred filter approaches over complex loops
Immediate debugging escalation when patterns fail
Systematic troubleshooting rather than trial-and-error approaches
Automatic timestamped backup creation before file modifications
Comprehensive testing verification through script-based testing
Secrets properly referenced via !secret syntax
Package sharing standards followed for community distribution