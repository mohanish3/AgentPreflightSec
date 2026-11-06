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
from agentpreflight.rules.ap_net import BroadBindRule, MissingOriginValidationRule, PlainHttpToolRule
from agentpreflight.rules.ap_sec_001 import PrivateKeyRule
from agentpreflight.rules.ap_sec_002 import ApiTokenRule, EnvFileRule
from agentpreflight.rules.ap_mcp_001 import McpPromptOverrideRule
from agentpreflight.rules.ap_skill_001 import SkillPromptInjectionRule
from agentpreflight.rules.ap_skill_002 import HiddenUnicodeRule
from agentpreflight.rules.ap_skill_more import (
    SkillCapabilityMismatchRule,
    SkillCredentialSeekingRule,
    SkillRemoteDependencyRule,
)
from agentpreflight.rules.ap_owasp import (
    InsecureDeserializationRule,
    PathTraversalRule,
    SqlInjectionRule,
    SsrfRule,
    TemplateInjectionRule,
)
from agentpreflight.rules.ap_dep_001 import DependencyVulnRule

ALL_RULES: list[Rule] = [
    # Code execution & injection
    UnsafeShellRule(),
    DynamicCodeExecRule(),
    RemoteScriptExecRule(),
    ArbitraryFileAccessRule(),
    NetworkExfiltrationRule(),
    # OWASP Top 10
    SqlInjectionRule(),
    PathTraversalRule(),
    InsecureDeserializationRule(),
    TemplateInjectionRule(),
    SsrfRule(),
    # Secrets
    PrivateKeyRule(),
    ApiTokenRule(),
    EnvFileRule(),
    # Dependencies
    DependencyVulnRule(),
    # MCP / Agent
    McpPromptOverrideRule(),
    McpTrustClaimRule(),
    McpUntrustedResultRule(),
    McpLooseSchemaRule(),
    McpPrivilegedToolRule(),
    # Skills / Markdown
    SkillPromptInjectionRule(),
    HiddenUnicodeRule(),
    SkillRemoteDependencyRule(),
    SkillCredentialSeekingRule(),
    SkillCapabilityMismatchRule(),
    # Network
    BroadBindRule(),
    MissingOriginValidationRule(),
    PlainHttpToolRule(),
]
