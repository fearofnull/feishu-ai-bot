# Quoted Message CLI Passthrough Bugfix Design

## Overview

The bug occurs when quoted card messages are sent to CLI executors. While the system successfully parses and combines quoted content with the current message, and updates `parsed_command.message` with the combined message, the CLI executor receives only the current message without the quoted content. This is caused by the CLI execution path using the original `user_prompt` parameter name instead of reading from the updated `parsed_command.message`. The fix requires ensuring that CLI executors receive the message from `parsed_command.message` rather than from an earlier variable that doesn't contain the quoted content.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when a user quotes a card message and sends it to a CLI executor
- **Property (P)**: The desired behavior - CLI executors should receive the complete combined message including quoted content
- **Preservation**: Existing behavior for non-quoted messages and API executors that must remain unchanged
- **parsed_command.message**: The ParsedCommand object's message field that contains the combined message after line 293
- **final_message**: The combined message created by `message_handler.combine_messages()` at line 282
- **CLI executor**: Executors that use command-line interfaces (e.g., GeminiCLIExecutor, ClaudeCLIExecutor)
- **API executor**: Executors that use API interfaces (e.g., OpenAI API, Claude API)

## Bug Details

### Fault Condition

The bug manifests when a user quotes a card message and directs it to a CLI executor. The system successfully parses the quoted content, combines it with the current message, and updates `parsed_command.message` with the combined message. However, the CLI execution path at line 354 passes `parsed_command.message` to `executor.execute()`, but the executor receives only the current message without the quoted content.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type MessageEvent
  OUTPUT: boolean
  
  RETURN input.has_quoted_card_message == True
         AND input.target_executor.type == "CLI"
         AND parsed_command.message contains combined message
         AND executor receives only current message (quoted content missing)
END FUNCTION
```

### Examples

- User quotes a card message containing error details and sends "@gemini-cli explain this error" → CLI receives only "explain this error" without the error details
- User quotes a summary card and sends "@gemini-cli 再总结一下上面的卡片内容" → CLI receives only "再总结一下上面的卡片内容" without the card content
- User quotes a card with code and sends "@gemini-cli fix this code" → CLI receives only "fix this code" without the code
- Edge case: User sends "@gemini-cli hello" without quoting → CLI should receive only "hello" (preservation requirement)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Messages without quoted content sent to CLI executors must continue to work exactly as before
- API executors must continue to receive combined messages correctly (this already works)
- Message parsing and combination logic must remain unchanged
- Bot reply formatting showing quoted context must remain unchanged

**Scope:**
All inputs that do NOT involve quoting card messages to CLI executors should be completely unaffected by this fix. This includes:
- Non-quoted messages to CLI executors
- Quoted messages to API executors (already working)
- Text message quoting (non-card messages)
- All message parsing and combination logic

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause has been identified:

**CONFIRMED ROOT CAUSE: Multi-line Message Format in CLI Headless Mode**

The `combine_messages()` method in `message_handler.py` was using newline characters (`\n\n`) to separate the quoted message and current message:

```python
combined = f"引用消息：{quoted}\n\n当前消息：{current}"
```

However, CLI executors (Gemini CLI, Claude CLI) running in headless mode do NOT support multi-line input. When the combined message with newlines is passed to the CLI command, the newlines cause the message to be truncated or improperly parsed, resulting in only the current message being passed to the CLI executor.

**The Fix:**

Change the message format to use a single-line separator instead of newlines:

```python
combined = f"引用消息：{quoted} | 当前消息：{current}"
```

This is consistent with the fix previously applied to `_prepend_language_instruction()` method, which also uses single-line format to avoid CLI headless mode issues.

**Previous Hypotheses (Incorrect):**

1. ~~Variable Shadowing or Incorrect Parameter~~: The CLI execution path correctly passes `parsed_command.message` to `executor.execute()`.

2. ~~ParsedCommand Recreation Issue~~: The new `ParsedCommand` object is correctly created with `message=final_message`.

3. ~~Executor Parameter Handling~~: The executor correctly receives the message parameter.

4. ~~Scope Issue~~: The `final_message` variable is correctly used throughout the function.

## Correctness Properties

Property 1: Fault Condition - CLI Executors Receive Combined Messages

_For any_ message event where a card message is quoted and directed to a CLI executor, the fixed code SHALL pass the complete combined message (format: "引用消息：{quoted}\n\n当前消息：{current}") to the CLI executor's execute method, ensuring the executor receives both the quoted card content and the current message text.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: Preservation - Non-Quoted Message Behavior

_For any_ message event where no card message is quoted OR the target is an API executor, the fixed code SHALL produce exactly the same behavior as the original code, preserving the existing message passing logic for non-quoted messages to CLI executors and all messages to API executors.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

**File**: `feishu_bot/core/message_handler.py`

**Function**: `combine_messages`

**Root Cause**: The method was using newline characters (`\n\n`) to format the combined message, but CLI executors running in headless mode do not support multi-line input.

**Specific Changes**:

Change the message format from multi-line to single-line:

```python
# Before (buggy):
combined = f"引用消息：{quoted}\n\n当前消息：{current}"

# After (fixed):
combined = f"引用消息：{quoted} | 当前消息：{current}"
```

This ensures the entire combined message is passed as a single line to the CLI executor, avoiding truncation or parsing issues in headless mode.

**Additional Changes**:

Add a note in the docstring to document this requirement:

```python
Note:
    使用单行格式，避免 CLI headless 模式的多行问题
```

### Why This Fix Works

1. **Single-line format**: By using ` | ` as a separator instead of `\n\n`, the entire message remains on a single line.

2. **Consistent with existing patterns**: This follows the same pattern used in `_prepend_language_instruction()` method, which also uses single-line format for CLI compatibility.

3. **Preserves all content**: The quoted content and current message are both included in the combined message, just formatted differently.

4. **CLI-compatible**: Single-line messages work correctly with both Gemini CLI and Claude CLI in headless mode.

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that simulate quoting a card message and sending it to a CLI executor. Add debug logging to trace the message value at key points: (1) after combination at line 283, (2) after ParsedCommand creation at line 293, (3) immediately before executor call at line 354, and (4) inside the executor's execute method. Run these tests on the UNFIXED code to observe where the quoted content is lost.

**Test Cases**:
1. **Quoted Card to CLI Test**: Quote a card message with content "Error: File not found" and send "@gemini-cli explain this" (will fail on unfixed code - CLI receives only "explain this")
2. **Quoted Card to API Test**: Quote the same card and send "@openai-api explain this" (should pass on unfixed code - API executors already work)
3. **Non-Quoted to CLI Test**: Send "@gemini-cli hello" without quoting (should pass on unfixed code - non-quoted messages work)
4. **Variable Trace Test**: Add logging at lines 283, 293, 354, and inside executor to trace where the message content changes (will reveal the root cause)

**Expected Counterexamples**:
- CLI executor receives only current message without quoted content
- Possible causes: variable shadowing at line 354, incorrect parameter passing, or intermediate processing that strips quoted content

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := _handle_message_receive_fixed(input)
  ASSERT cli_executor_received_message contains quoted_content
  ASSERT cli_executor_received_message contains current_message
  ASSERT cli_executor_received_message == combined_message
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT _handle_message_receive_original(input) = _handle_message_receive_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for non-quoted messages and API executors, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Non-Quoted CLI Preservation**: Observe that non-quoted messages to CLI executors work correctly on unfixed code, then write test to verify this continues after fix
2. **API Executor Preservation**: Observe that quoted messages to API executors work correctly on unfixed code, then write test to verify this continues after fix
3. **Message Parsing Preservation**: Observe that message parsing and combination logic works correctly on unfixed code, then write test to verify this continues after fix
4. **Bot Reply Preservation**: Observe that bot replies show quoted context correctly on unfixed code, then write test to verify this continues after fix

### Unit Tests

- Test that `parsed_command.message` contains combined message after line 293
- Test that CLI executor receives the same message value as `parsed_command.message`
- Test that non-quoted messages to CLI executors receive only current message
- Test that API executors continue to receive combined messages correctly

### Property-Based Tests

- Generate random quoted card messages with various content types and verify CLI executors receive complete combined messages
- Generate random non-quoted messages and verify CLI executors receive only current message (preservation)
- Generate random messages to API executors and verify they continue to work correctly (preservation)

### Integration Tests

- Test full flow: quote card message → send to CLI executor → verify CLI receives combined message
- Test full flow: send non-quoted message to CLI executor → verify CLI receives only current message
- Test full flow: quote card message → send to API executor → verify API receives combined message (preservation)
- Test that CLI execution logs show the complete combined message content
