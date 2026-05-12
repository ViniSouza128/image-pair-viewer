# Sample image credits

The `samples/` folder contains 4 before/after pairs used by the **"Try with sample images"** button on the upload screen. They let visitors test the comparison tool without uploading their own photos.

For each pair, the **"before"** is the original photo (downscaled to 2000 px on the long side); the **"after"** is a derivative produced by photographic edits (color grading, contrast, sharpening, vignette) generated locally by [`_samples_build.py`](_samples_build.py). The point of the edits is to demonstrate the comparison tool, not to substitute real-world photo retouching.

All sources are either **Public Domain** or **CC BY-SA 4.0** — both permit reuse for any purpose, including commercial. CC BY-SA 4.0 derivatives must remain CC BY-SA 4.0 (which they are here).

---

## 1. Foggy winter morning (`sample_0001_foggy-morning*.jpg`)

- **Author**: Soumyajit Nandy
- **License**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Source**: [File:A foggy winter morning.jpg on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:A_foggy_winter_morning.jpg)
- **Edit applied** ("after"): dehaze (contrast +55%, saturation +45%, slight warm tint, unsharp mask)

## 2. Aerial image of Grand Prismatic Spring (`sample_0002_prismatic-spring*.jpg`)

- **Author**: Jim Peaco / National Park Service
- **License**: [Public Domain](https://en.wikipedia.org/wiki/Copyright_status_of_works_by_the_federal_government_of_the_United_States) (work of US federal government employee)
- **Source**: [File:Aerial image of Grand Prismatic Spring (view from the south).jpg on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Aerial_image_of_Grand_Prismatic_Spring_(view_from_the_south).jpg)
- **Edit applied** ("after"): vibrant grade (contrast +35%, saturation +65%, blue boost in midtones, sharpening)

## 3. Henry Espinoza Panta smashing a wave at Lobitos (`sample_0003_surfer-wave*.jpg`)

- **Author**: Marco Garro
- **License**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Source**: [File:Henry Espinoza Panta smashing a wave at Lobitos.jpg on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Henry_Espinoza_Panta_smashing_a_wave_at_Lobitos.jpg)
- **Edit applied** ("after"): cinematic teal/orange grade (contrast +30%, saturation +15%, color split-tone, radial vignette)

## 4. F-35 Heritage Flight Team (`sample_0004_f35-airshow*.jpg`)

- **Author**: Senior Airman Tristen W. Webb / U.S. Air Force
- **License**: [Public Domain](https://en.wikipedia.org/wiki/Copyright_status_of_works_by_the_federal_government_of_the_United_States) (work of US federal government employee)
- **Source**: [File:F-35 Heritage Flight Team performs in Bell Fort Worth Alliance AirShow.jpg on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:F-35_Heritage_Flight_Team_performs_in_Bell_Fort_Worth_Alliance_AirShow.jpg)
- **Edit applied** ("after"): aviation-style punchy (contrast +40%, saturation +30%, deep-blue sky boost, strong unsharp mask)

---

## Regenerating the samples

```bash
python _samples_build.py
```

Downloads originals, resizes to 2000 px, and writes both `before` and `after` JPEGs plus an updated `manifest.json` into `samples/`.

---

## Licensing summary

- **Project code** (`index.html`, `_build.py`, `_samples_build.py`): see [LICENSE](LICENSE).
- **Sample images** (`samples/*.jpg`): individually licensed as listed above (CC BY-SA 4.0 or Public Domain). Attribution requirements for CC BY-SA images are satisfied by this file.
