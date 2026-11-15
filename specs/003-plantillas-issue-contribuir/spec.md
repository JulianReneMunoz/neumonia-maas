# SPEC-003 · Plantillas de historia de usuario y guía de contribución

- **Estado:** Borrador <!-- Borrador → Aprobada → Implementada -->
- **Historia:** #? (confirmar con `uv run scripts/tablero.py issue SPEC-003`) · **Puntos:** 1 · **Milestone:** M3 · **Labels:** kanban, docs
- **Depende de:** SPEC-001
- **PR:** #N (se completa al abrirla)

## 1. Problema y contexto
El kit inicial ya trae `.github/ISSUE_TEMPLATE/` (`historia.yml`, `bug.yml`, `config.yml`) y
`.github/PULL_REQUEST_TEMPLATE.md`, pero nadie ha verificado que cumplan lo que pide la
historia, no remiten a ninguna guía y **no existe `CONTRIBUTING.md`**: el flujo de trabajo,
los WIP limits y la Definition of Done solo están dispersos en `CLAUDE.md`,
`docs/plan-semana.md`, `scripts/ghlib.py` y el README del Project (`scripts/completar_tablero.py`).
Para el equipo importa porque cada tarjeta nueva debe nacer con Como/quiero/para, AC
Given-When-Then, puntos y ruta de la spec, sin depender de la memoria de nadie. Para la
rúbrica, `scripts/auditar_rubrica.py` asigna a SPEC-003 los ítems D1–D6 (tablero, WIP
escritos, historias con AC y Fibonacci 1:1, historia → spec, PR con `Closes #N`, métricas) y
E4 (Conventional Commits y plantilla de PR): esta historia deja esa evidencia escrita en el repo.

## 2. Historia
**Como** integrante del equipo, **quiero** una plantilla de issue para historias y un
CONTRIBUTING con el flujo **para** que toda tarjeta tenga Como/quiero/para, AC
Given-When-Then, puntos y spec.

## 3. Requisitos
### Funcionales
- RF-1: `.github/ISSUE_TEMPLATE/historia.yml` es un *issue form* válido de GitHub llamado
  «Historia de usuario» con, como mínimo, estos campos y `validations.required: true`:
  `historia` (textarea, Como/quiero/para), `ac` (textarea, Given-When-Then), `puntos`
  (dropdown con exactamente las opciones `1`, `2`, `3`, `5`, `8`) y `spec` (input con la ruta
  `specs/NNN-slug/`). El campo `dependencias` existe y es opcional.
- RF-2: El título por defecto de una historia empieza por `SPEC-NNN` (compatible con
  `spec_de_titulo()` de `scripts/ghlib.py`).
- RF-3: `historia.yml` incluye un bloque `markdown` inicial que remite a `CONTRIBUTING.md` y
  recuerda la regla 1:1 (issue = tarjeta = spec = PR).
- RF-4: `.github/ISSUE_TEMPLATE/bug.yml` es un issue form válido con label `bug` (ya
  creado por `bootstrap_github.py`) y los campos obligatorios «Pasos para reproducir» y
  «Resultado esperado y obtenido»; «Spec afectada» queda opcional.
- RF-5: `.github/ISSUE_TEMPLATE/config.yml` desactiva los issues en blanco
  (`blank_issues_enabled: false`) y ofrece un `contact_links` a `CONTRIBUTING.md`.
- RF-6: Existe `CONTRIBUTING.md` en la raíz con, al menos, estas secciones:
  1. **Flujo** Backlog → spec → rama → PR → review → merge → Done, con los comandos del
     repo (`/siguiente`, `/spec`, `/implementar`, `/pr`, `/revisar`, `/fusionar`) y qué pasa
     con la tarjeta en cada paso.
  2. **Columnas y WIP limits**: Backlog (sin límite), In Progress (WIP = nº de
     integrantes; hoy 1), In Review (WIP 2), Done; y la regla «si la columna está llena, no
     se empieza otra historia».
  3. **Definition of Done** con los seis puntos de `CLAUDE.md`.
  4. **Gitflow**: ramas `feature/NNN-slug` desde `develop`, nada directo a `main`/`develop`,
     sin `--no-verify` ni `push --force`.
  5. **Conventional Commits** con el ID de la spec, con ejemplos.
  6. **Cómo crear una historia** (plantilla «Historia de usuario», puntos Fibonacci, ruta de
     la spec) y **cómo abrir la PR** (plantilla existente, `Closes #N`).
  7. **Reglas no negociables** resumidas (uv, sin Streamlit/notebooks, tres capas, pruebas
     AAA sin red, sin secretos ni datos de pacientes), remitiendo a `CLAUDE.md`.
- RF-7: El `README.md` enlaza `CONTRIBUTING.md` en su sección «Enlaces» (una línea).

### No funcionales
- RNF-1: Una sola fuente de verdad para los números de WIP: los valores de `CONTRIBUTING.md`
  coinciden con `scripts/ghlib.py` (`WIP_REVIEW = 2`) y `docs/tablero.json` (`integrantes`).
- RNF-2: Todo en español; los YAML se guardan en UTF-8 y parsean con un parser YAML estándar.
- RNF-3: No se duplica `PULL_REQUEST_TEMPLATE.md`: CONTRIBUTING lo enlaza, no lo copia.
- RNF-4: Sin secretos, URLs privadas ni datos de pacientes en plantillas ni guía.
- RNF-5: `make check` (ruff + pytest de SPEC-001) sigue en verde.

## 4. Criterios de aceptación (Given-When-Then)
**AC-1** (backlog)
- **Dado** el botón «New issue» del repositorio
- **Cuando** elijo «Historia de usuario»
- **Entonces** el formulario exige historia, AC, puntos Fibonacci y ruta de la spec

**AC-2** (backlog)
- **Dado** `CONTRIBUTING.md`
- **Cuando** lo leo
- **Entonces** describe el flujo Backlog → spec → rama → PR → review → merge → Done, los WIP
  limits y la DoD

**AC-3** (añadido: puntos solo Fibonacci)
- **Dado** el formulario «Historia de usuario»
- **Cuando** despliego «Estimación (Fibonacci)»
- **Entonces** solo puedo elegir 1, 2, 3, 5 u 8 y no puedo enviar el issue sin elegir uno

**AC-4** (añadido: sin issues en blanco)
- **Dado** el botón «New issue»
- **Cuando** veo el selector de plantillas
- **Entonces** solo aparecen «Historia de usuario», «Bug» y el enlace a la guía de
  contribución; no hay opción de issue en blanco

**AC-5** (añadido: bug con campos mínimos)
- **Dado** el formulario «Bug»
- **Cuando** intento enviarlo sin pasos para reproducir o sin resultado esperado/obtenido
- **Entonces** GitHub no lo deja enviar y, al crearlo, el issue queda con el label `bug`

**AC-6** (añadido: YAML válidos)
- **Dado** los tres archivos de `.github/ISSUE_TEMPLATE/`
- **Cuando** los abro en GitHub (vista del archivo en la rama) o los parseo con un parser YAML
- **Entonces** no hay errores de sintaxis ni de esquema del issue form

**AC-7** (añadido: WIP coherente)
- **Dado** `CONTRIBUTING.md`, `scripts/ghlib.py` y `docs/tablero.json`
- **Cuando** comparo los WIP limits
- **Entonces** In Progress = `integrantes` (1) e In Review = `WIP_REVIEW` (2) en los tres

**AC-8** (añadido: guía localizable)
- **Dado** el `README.md`
- **Cuando** busco cómo contribuir
- **Entonces** encuentro un enlace a `CONTRIBUTING.md`, y CONTRIBUTING enlaza la plantilla de
  PR, `CLAUDE.md`, `docs/backlog.yaml` y `docs/plantillas-sdd/`

## 5. Fuera de alcance
- Crear o modificar el Project, sus columnas, campos o labels (lo hacen `bootstrap_github.py`
  y `completar_tablero.py`).
- Reescribir `PULL_REQUEST_TEMPLATE.md` (ya existe y cubre `Closes #N`, spec, AC y DoD).
- Protección de ramas, CI (SPEC-002) y pre-commit (SPEC-036).
- Explicación detallada de las métricas del tablero (SPEC-040); aquí solo se nombran y se
  remite a `uv run scripts/tablero.py metricas`.
- README definitivo (SPEC-037); aquí solo se añade un enlace.
- `CODE_OF_CONDUCT.md`, `SECURITY.md` u otras plantillas de comunidad.

## 6. Métricas de éxito
- 100 % de los issues creados desde el formulario tienen los cuatro campos obligatorios llenos.
- 0 opciones de issue en blanco en el selector de GitHub.
- `CONTRIBUTING.md` contiene las 7 secciones de RF-6 y se puede leer en menos de 5 minutos.
- `make check` en verde tras la PR.

## 7. Preguntas abiertas
1. **Las plantillas ya existen** (vienen en el kit inicial y ya están en `develop`, la rama
   por defecto). El plan las **ajusta** (bloque `markdown`, `contact_links`) en vez de
   crearlas. ¿De acuerdo con tocar archivos del kit en esta PR?
2. **Prueba automática opcional.** El piso es 0 pruebas. El plan propone 3 pruebas pytest sin
   red que parsean los YAML y verifican los `required`; necesitan PyYAML como dependencia de
   desarrollo (`uv add --dev pyyaml`). ¿Se incluyen (suman al conteo de ≥ 120 pruebas) o se
   deja la historia en 0 pruebas?
3. **Demo del AC-1/AC-4/AC-5.** GitHub solo usa las plantillas de la rama por defecto
   (`develop`), así que el formulario «real» con los cambios se ve después del merge. Antes,
   la demo usa la vista previa del archivo `.yml` en la rama. ¿Es aceptable?
4. **Número del issue** de SPEC-003 en GitHub para el encabezado y `Closes #N`: confirmarlo al
   abrir la PR.
