from pathlib import Path

import yaml


class PolicyEngine:
    def __init__(self, policy_file: str):
        self.policy_file = Path(policy_file).resolve()

        with open(self.policy_file, "r") as f:
            self.policy = yaml.safe_load(f)

    def is_allowed(
        self,
        identity: str,
        action: str,
        resource: str,
        attributes: dict,
    ) -> bool:

        roles = self.policy.get("roles", {})
        permissions = roles.get(identity, {})

        allowed_resources = permissions.get(action, [])

        if not allowed_resources:
                return False

    # Vérification des règles ABAC
        action_rules = self.policy.get("rules", {}).get("actions", {})
        action_rule = action_rules.get(action, {})

        requirements = action_rule.get("require", {})

        for attribute, expected_value in requirements.items():
            actual_value = attributes.get(attribute)

            if actual_value != expected_value:
                return False

    # Vérification de la ressource
        requested_path = Path(resource).expanduser().resolve()

        for allowed_resource in allowed_resources:
            allowed_path = Path(allowed_resource).expanduser().resolve()

            try:
                requested_path.relative_to(allowed_path)
                return True
            except ValueError:
                continue

        return False

    def audit_log(
        self,
        identity: str,
        action: str,
        resource: str,
        attributes: dict,
        decision: str,
    ):
        print(
            f"[AUDIT] identity={identity} "
            f"action={action} "
            f"resource={resource} "
            f"attributes={attributes} "
            f"decision={decision}"
        )
