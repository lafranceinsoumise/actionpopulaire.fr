import rules


@rules.predicate
def is_pending_voting_proxy_request(role, obj):
    return obj is not None and obj.is_pending()


rules.add_perm(
    "voting_proxies.view_voting_proxy_request",
    is_pending_voting_proxy_request,
)
