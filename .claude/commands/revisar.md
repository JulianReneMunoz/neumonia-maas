---
description: Revisión de código de una PR contra su spec (subagente code-reviewer)
argument-hint: <número de PR>
---
PR: **#$ARGUMENTS**

1. Delega en el subagente **code-reviewer** la revisión de la PR #$ARGUMENTS.
   Debe leer `gh pr view $ARGUMENTS`, `gh pr diff $ARGUMENTS`, la spec enlazada y
   `gh pr checks $ARGUMENTS`, y devolver un informe con veredicto APROBAR o CAMBIOS.
2. Publica el informe en la PR:
   - si quien revisa es otra persona con acceso (compañero o profesor), pídele que apruebe
     desde GitHub con base en el informe;
   - si no, publícalo como comentario: `gh pr review $ARGUMENTS --comment --body-file <archivo temporal>`
     (GitHub no deja aprobar la PR propia).
3. Si el veredicto es CAMBIOS, propone los arreglos, impleméntalos en la misma rama con
   commits `fix:`/`refactor:`, haz push y repite la revisión.
4. Si es APROBAR y los checks están verdes, sugiere `/fusionar $ARGUMENTS`.
