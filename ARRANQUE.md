# ARRANQUE — de cero a la primera historia (≈ 45 min)

Hazlo **una vez, en orden**. Los comandos son para PowerShell (Windows). Todo lo que dice
«a mano» se hace en tu terminal, **fuera de Claude Code**: la guardia del kit bloquea a
Claude los commits directos a `main`/`develop`, y eso es lo que queremos.

## 0 · Antes de empezar (3 decisiones que no son mías)
1. **Confirma con el profesor** cómo se cuenta este trabajo: cómo se califica la
   reprogramación del M3, si el repo nuevo reemplaza al anterior y si los 40 PRs/specs
   pueden hacerse esta semana. La sustentación es el **jueves 19/11**; confirma la **hora** y el salón.
2. **Revisión de código en un grupo de una persona.** La regla exige que un compañero
   apruebe cada PR; tu grupo (G8) tiene un solo integrante. Pregúntale al profesor cómo se
   cumple (¿reviewer asignado por él? ¿acepta el informe del subagente `code-reviewer`
   publicado en la PR?). No lo resuelvas con cuentas inventadas: es justo lo que la
   rúbrica penaliza («auto-merges sin revisión»).
3. **Nombre del repo** y tu usuario de GitHub (abajo uso `JulianReneMunoz/neumonia-maas`;
   cámbialo si es otro).

## 1 · Herramientas (una sola vez)
```powershell
winget install --id Git.Git -e
winget install --id GitHub.cli -e
winget install --id astral-sh.uv -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Docker.DockerDesktop -e      # lo necesitas el miércoles 18
corepack enable; corepack prepare pnpm@latest --activate
```
Cierra y abre PowerShell. Verifica: `git --version; gh --version; uv --version; node -v; pnpm -v`.
Claude Code ya lo tienes; si no: https://claude.com/claude-code

## 2 · Carpeta `C:\Neumonia` y primer commit (a mano)
**Primero mira qué hay hoy en `C:\Neumonia`** (mis notas dicen que ahí vive el proyecto anterior, con Streamlit):
```powershell
git -C C:\Neumonia remote -v
git -C C:\Neumonia status -sb
```
- Si el remoto es `JulianReneMunoz/Neumonia` (o hay carpeta `src\neumonia` con Streamlit) → es el proyecto **viejo**: sigue el **2A**.
- Si la carpeta está vacía o solo tiene el kit → salta al **2B**.

### 2A · Apartar el proyecto viejo sin perder nada (2 minutos)
Cierra VS Code, cualquier `streamlit`, `mlflow` o terminal abierta en esa carpeta, y entonces:
```powershell
cd C:\
Rename-Item C:\Neumonia Neumonia_viejo          # renombrar es instantáneo; conserva ramas, stash, .venv y datos
$zip = "RUTA\neumonia-maas-kit.zip"            # tu navegador guarda en Documents\Neumonia o Descargas: ajusta
Expand-Archive $zip -DestinationPath C:\kit_tmp
Move-Item C:\kit_tmp\neumonia-maas C:\Neumonia
Remove-Item C:\kit_tmp
# datos de RSNA (ya preparados en el proyecto viejo) → a la carpeta ignorada por Git
New-Item -ItemType Directory C:\Neumonia\data\raw -Force | Out-Null
if (Test-Path C:\Neumonia_viejo\data\raw\rsna) { Move-Item C:\Neumonia_viejo\data\raw\rsna C:\Neumonia\data\raw\rsna }
if (Test-Path C:\Neumonia_viejo\data\rsna)      { Move-Item C:\Neumonia_viejo\data\rsna C:\Neumonia\data\raw\rsna_csv }   # rsna_eval_500.csv y rsna_boxes.csv
```
`C:\Neumonia_viejo` queda como archivo (ahí siguen tu stash «rsna en curso», `demo/tomografia` y los parches). **No lo borres y no lo uses como repo del M3.** El repo viejo en GitHub tampoco se toca.

### 2B · Primer commit
```powershell
cd C:\Neumonia
Test-Path .git      # debe decir False; si dice True, vuelve al 2A: no se hace `git init` sobre un repo viejo
git init -b main
git add -A
git commit -m "chore: kit inicial (backlog, plantillas, comandos de Claude Code)"
```
(`data\raw\` está en `.gitignore`: los datos de RSNA no se suben.)

## 3 · Repositorio en GitHub
```powershell
gh auth login                                   # GitHub.com → HTTPS → navegador
gh repo create JulianReneMunoz/neumonia-maas --private --source . --remote origin --push
gh api -X PUT repos/JulianReneMunoz/neumonia-maas/collaborators/USUARIO_DEL_PROFESOR -f permission=pull
```
(El usuario del profesor te lo da él. Si el Project y el repo son privados, **debe estar invitado**.)

## 4 · Tablero, issues y milestones (el script lo crea todo)
```powershell
uv run scripts/bootstrap_github.py --repo JulianReneMunoz/neumonia-maas --integrantes 1 --dry-run
uv run scripts/bootstrap_github.py --repo JulianReneMunoz/neumonia-maas --integrantes 1
```
Crea labels, milestones M3/M4, el Project con las 4 columnas (el WIP va en la descripción de
cada columna), y **45 issues** (40 del M3 + 5 provisionales del M4) con su historia, AC y
puntos. Si falla a la mitad, vuelve a correrlo: no duplica.

Si `gh` pide permiso para proyectos: `gh auth refresh -s project` y repite.

Luego, en el navegador: abre el Project → vista **Board** agrupada por *Status* → el tablero
queda con Backlog / In Progress / In Review / Done. Hazlo visible:
```powershell
gh project list --owner JulianReneMunoz           # anota el número
gh project edit NUMERO --owner JulianReneMunoz --visibility PUBLIC
```

## 5 · Ramas (Gitflow) y cierre del arranque (a mano)
```powershell
git add docs/tablero.json
git commit -m "chore: configuración del tablero"
git push origin main
git switch -c develop
git push -u origin develop
gh repo edit JulianReneMunoz/neumonia-maas --default-branch develop
```
**¿Por qué `develop` como rama por defecto?** GitHub solo cierra automáticamente el issue
de `Closes #N` cuando la PR se fusiona en la rama por defecto. Sin esto, las tarjetas
quedarían abiertas.

Estos dos commits directos (kit y tablero) son el arranque del repo. A partir de aquí, **todo
entra por PR**. Cuéntaselo al profesor antes de que lo pregunte.

## 6 · Primera historia con Claude Code
```powershell
cd C:\Neumonia
claude
```
Dentro de Claude Code:
1. `/hooks` → debe aparecer el hook `PreToolUse` de `guardia.py`. Prueba: pídele
   «ejecuta pip install requests» → debe **bloquearlo**.
2. `/siguiente` → te propone SPEC-001.
3. `/spec SPEC-001` → crea la rama, escribe spec/plan/tasks y **se detiene**. Léelos.
   Cuando estén bien: «aprobada».
4. `/implementar SPEC-001` → TDD tarea por tarea. Al final te explica y te hace una pregunta.
   **Respóndela**: eso es la defensa individual.
5. `/pr SPEC-001` → abre la PR con `Closes #N`.
6. `/revisar <n>` y `/fusionar <n>` (ver revisión de código en el punto 0.2).

Con SPEC-002 fusionada, protege las ramas (necesita que el check `ci` ya exista):
```powershell
gh api -X PUT repos/JulianReneMunoz/neumonia-maas/branches/develop/protection --input docs/proteccion-rama.json
gh api -X PUT repos/JulianReneMunoz/neumonia-maas/branches/main/protection    --input docs/proteccion-rama.json
```
(Repos privados en plan gratuito pueden no soportar la protección de ramas; si GitHub lo
rechaza, la guardia de Claude Code y la disciplina de PRs la reemplazan, y lo explicas.)

## 7 · Rutina diaria (~9 historias al día)
Plazo: **jueves 19/11**, todo listo el **miércoles 18**. Ver `docs/plan-semana.md`.
Cada bloque: `/lote SPEC-a SPEC-b SPEC-c SPEC-d` (specs de corrido) → *lees y apruebas* → por historia
`/implementar` → *respondes la pregunta* → `/pr` → `/revisar` → `/fusionar`. Nunca más de una historia en implementación a la vez.
Si quieres ir más pausado en la primera historia, usa `/siguiente` y `/spec SPEC-001` para ver el flujo completo.

Cada noche: `/tablero` (métricas) y `uv run scripts/auditar_rubrica.py` (cobertura del checklist). `/ensayo` el martes y el miércoles; el guion está en `docs/guion-sustentacion.md` y la ficha en `docs/ficha-entrega.md`.

**Pendiente de la clase (no lo invento):** Archify, el hook GGA y Engram aparecen en el anuncio (Archify es obligatorio, GGA y Engram son «deseable»). Trae el material de las Clases 7–9 y pídele a Claude Code que los integre siguiendo esas instrucciones.

## 8 · Si algo se rompe
| Síntoma | Qué hacer |
|---|---|
| `uv` no encuentra Python 3.13 | `uv python install 3.13` |
| `gh project …` da 403 | `gh auth refresh -s project,read:project` |
| Descarga del modelo falla | Revisa red/proxy; el modelo se baja una vez a `~/.cache/huggingface` |
| El hook bloquea algo legítimo | Léelo: casi siempre es una regla del curso. Si de verdad es un falso positivo, corrige `.claude/hooks/guardia.py` **en una PR** |
| Claude propone saltarse la spec | Respóndele «no: `/spec` primero». La spec antes del código es lo que cuenta |
