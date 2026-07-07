from agentpreflight.rules.engine import Rule
from agentpreflight.rules.ap_code_001 import UnsafeShellRule
from agentpreflight.rules.ap_code_002 import DynamicCodeExecRule
from agentpreflight.rules.ap_code_003 import RemoteScriptExecRule
from agentpreflight.rules.ap_code_more import ArbitraryFileAccessRule, NetworkExfiltrationRule
from agentpreflight.rules.ap_mcp_more import (
    McpLooseSchemaRule,
    McpPrivilegedToolRule,
    McpTrustClaimRule,
    McpUntrustedResultRule,
)
from agentpreflight.rules.ap_mcp_001 import McpPromptOverrideRule
from agentpreflight.rules.ap_mcp_002 import HiddenUnicodeInDescriptionRule
from agentpreflight.rules.ap_net import BroadBindRule, MissingOriginValidationRule, PlainHttpToolRule
from agentpreflight.rules.ap_sec_001 import PrivateKeyRule
from agentpreflight.rules.ap_sec_002 import ApiTokenRule, EnvFileRule
from agentpreflight.rules.ap_skill_001 import SkillPromptInjectionRule
from agentpreflight.rules.ap_skill_002 import HiddenUnicodeRule
from agentpreflight.rules.ap_skill_more import (
    SkillCapabilityMismatchRule,
    SkillCredentialSeekingRule,
    SkillRemoteDependencyRule,
)

ALL_RULES: list[Rule] = [
    UnsafeShellRule(),
    DynamicCodeExecRule(),
    RemoteScriptExecRule(),
    ArbitraryFileAccessRule(),
    NetworkExfiltrationRule(),
    PrivateKeyRule(),
    ApiTokenRule(),
    EnvFileRule(),
    McpPromptOverrideRule(),
    HiddenUnicodeInDescriptionRule(),
    McpTrustClaimRule(),
    McpUntrustedResultRule(),
    McpLooseSchemaRule(),
    McpPrivilegedToolRule(),
    SkillPromptInjectionRule(),
    HiddenUnicodeRule(),
    SkillRemoteDependencyRule(),
    SkillCredentialSeekingRule(),
    SkillCapabilityMismatchRule(),
    BroadBindRule(),
    MissingOriginValidationRule(),
    PlainHttpToolRule(),
]
