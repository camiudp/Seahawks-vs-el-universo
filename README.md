# Seahawks vs. el Universo 🏈🌌

Un sitio chistoso de "correlaciones espurias" al estilo
[tylervigen.com/spurious-correlations](https://www.tylervigen.com/spurious-correlations),
pero con los Seattle Seahawks como protagonistas.

Cruza los 85 partidos de temporada regular de los Seahawks (2021–2025) contra
cuatro series de datos reales que no tienen absolutamente nada que ver con el
fútbol americano:

- ❄️ Cobertura de nieve del hemisferio norte (mensual)
- ₿ Precio del bitcoin (mensual)
- 🚀 Lanzamientos de cohetes en todo el mundo (mensual)
- 🌕 Porcentaje de iluminación de la luna (por fecha exacta de partido)

Todo con humor, con la aclaración constante de que correlación no implica
causalidad — ese es justamente el chiste.

## Publicarlo en GitHub Pages

1. Crea un repositorio nuevo en GitHub (público, si quieres usar GitHub Pages
   gratis).
2. Sube todo el contenido de esta carpeta a la raíz del repo:

   ```bash
   git init
   git add .
   git commit -m "Seahawks vs. el Universo"
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
   git push -u origin main
   ```

3. En GitHub, ve a **Settings → Pages**.
4. En "Build and deployment" → "Source", elige **Deploy from a branch**.
5. Elige la branch `main` y la carpeta `/ (root)`, y guarda.
6. En un par de minutos el sitio queda disponible en:
   `https://<tu-usuario>.github.io/<tu-repo>/`

No necesita build ni dependencias de servidor — es HTML/CSS/JS estático. El
único recurso externo es [Chart.js](https://www.chartjs.org/) cargado desde
cdnjs.

## Estructura

```
index.html   → la página (estructura + contenido)
app.js       → arma los gráficos, las tarjetas de estadísticas, el ranking y la tabla
data.js      → el dataset ya procesado (generado por data/build_data.py)
data/
  build_data.py          → script que arma el dataset y calcula las correlaciones
  seahawks_universe.json → salida del script (la misma data que carga data.js)
```

Para regenerar `data.js` después de editar `data/build_data.py`:

```bash
cd data
python3 build_data.py
echo -n "const DATA = " > ../data.js
cat seahawks_universe.json >> ../data.js
echo ";" >> ../data.js
```

## Fuentes de datos

- **Resultados de los Seahawks**: artículos de temporada de Wikipedia
  (`en.wikipedia.org/wiki/<año>_Seattle_Seahawks_season`), verificados contra
  el récord final de cada temporada.
- **Nieve del hemisferio norte**: [Rutgers University Global Snow Lab](https://climate.rutgers.edu/snowcover/),
  cobertura mensual en km².
- **Precio de bitcoin**: [officialdata.org/bitcoin-price](https://officialdata.org/bitcoin-price),
  precio al primer día de cada mes.
- **Lanzamientos de cohetes**: [Launch Library 2](https://ll.thespacedevs.com/2.2.0/) de
  The Space Devs, conteo mensual global (todo tipo de lanzamientos).
- **Iluminación lunar**: calculada localmente con la aproximación estándar
  del mes sinódico (29.53058867 días), sin depender de ninguna API.

Los valores de nieve, bitcoin y lanzamientos son mensuales (se repiten para
todos los partidos jugados ese mes); la luna es el único dato calculado por
fecha exacta de partido.

## Licencia

Hazlo tuyo, modifícalo, cambia el equipo o las series de datos — es tu
repositorio.
