# Ficha de entrega previa (anuncio 007, sección 10)

Se envía por el WhatsApp del curso o al correo institucional **antes de la hora límite que fije el
profesor para la sustentación del jueves 19/11**. Complétala el miércoles 18.

| Dato | Qué enviar |
|---|---|
| Repositorio | `https://github.com/JulianReneMunoz/neumonia-maas` (profesor invitado; `develop` al día) |
| Kanban | URL del Project (público o profesor invitado) |
| Frontend | React + TypeScript (Vite) · `make frontend` (pnpm dev) → http://localhost:5173 |
| Backend | FastAPI · `make backend` · puerto 8000 · http://127.0.0.1:8000/docs |
| MLflow | `make mlflow` · puerto 5050 · `MLFLOW_TRACKING_URI=http://127.0.0.1:5050` |
| Modelo MaaS | `lxyuan/vit-xray-pneumonia-classification@<sha>` · Apache-2.0 · enlace a la Model Card del Hub |
| Model Card propia | `docs/model-card.md` |
| Archify | `docs/arquitectura.html` · tipo: _(el elegido)_ |
| PRs fusionadas | _N_ (todas de un solo integrante) |
| Especificaciones SDD | `specs/` · _N_ (≥ 40) · SPEC-001, SPEC-002 |

Verifica los números con: `gh pr list --state merged --limit 100 | wc -l` y
`find specs -name spec.md | wc -l`.
