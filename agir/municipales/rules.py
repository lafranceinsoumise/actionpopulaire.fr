import rules


@rules.predicate
def is_chef_de_file(role, obj):
    return (
        obj
        and obj.published
        and getattr(role, "person", None)
        and role.person in obj.municipales2020_admins.filter()
    )


rules.add_perm("municipales.change_communepage", is_chef_de_file)
