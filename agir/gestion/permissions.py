def peut_voir_montant_depense(user, depense):
    return (
        not depense.finalise
        or user.has_perm("gestion.voir_montant_depense")
        or user.has_perm("gestion.voir_montant_depense", depense.compte)
    )
