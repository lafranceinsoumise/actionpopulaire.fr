import rules


@rules.predicate
def is_pending_voting_proxy_request(role, obj):
    return obj is not None and obj.is_pending()


@rules.predicate
def is_voting_proxy_available_for_request(role, obj):
    voting_proxy = role.person.voting_proxy

    return (
        voting_proxy is not None
        and voting_proxy.is_available()
        and obj.email != voting_proxy.email
        and obj.voting_date.strftime("%Y-%m-%d") in voting_proxy.available_voting_dates
    )


rules.add_perm(
    "voting_proxies.view_voting_proxy_request",
    is_pending_voting_proxy_request & is_voting_proxy_available_for_request,
)
