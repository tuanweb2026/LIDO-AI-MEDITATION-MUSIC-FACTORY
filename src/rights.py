import sys

class SecurityGuardViolation(Exception):
    pass

class RightsReviewFailure(Exception):
    pass

def enforce_dry_run_guards(action_name):
    """Hard action restrictions in Phase 0."""
    unauthorized_actions = [
        "PUBLISH_VIDEO",
        "UPLOAD_AUDIO",
        "POST_COMMENT",
        "EXECUTE_AD_CAMPAIGN",
        "PURCHASE_SERVICE",
        "DOWNLOAD_MEDIA_CONTENT",
        "SCRAPE_WEBSITE"
    ]
    if action_name in unauthorized_actions:
        raise SecurityGuardViolation(
            f"BLOCKED: Action '{action_name}' is explicitly forbidden under Phase 0 dry-run policy."
        )

def verify_creative_brief_rights(brief_data):
    """Verify that generated creative brief is 100% original and uses no third-party melodies."""
    if brief_data.get("third_party_melody_used", False):
        raise RightsReviewFailure("REJECTED: Creative brief utilizes third-party melody or copyrighted samples.")
    if not brief_data.get("original_work_certified", False):
        raise RightsReviewFailure("REJECTED: Creative brief lacks original work certification.")
    return True
