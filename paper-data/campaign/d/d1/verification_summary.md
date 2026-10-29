# HronTurek verification summary

## monolithicAMI mesh study

- Result: FAIL
- monolithicAMI_mesh_2x: ux_mean = -0.00257765 differs from the reference -0.00288 by 10.50% (tolerance 10%)
- monolithicAMI_mesh_2x: uy_amplitude = 0.032798 differs from the reference 0.03499 by 6.26% (tolerance 5%)
- monolithicAMI_mesh_2x: 23864 cells, dt = 0.0005 s, 4 uy periods in the analysis window
- Data: `monolithicAMI_mesh_sweep.csv`

| Quantity | 2 | Featflow L4 | Turek-Hron 2006 | Tukovic 2018 | Turek-Hron history |
|---|---:|---:|---:|---:|---:|
| ux mean (mm) | -2.578 | -2.880 | -2.690 | -2.720 | -2.865 |
| ux amplitude (mm) | 2.452 | 2.720 | 2.530 | 2.580 | 2.703 |
| ux frequency (Hz) | 11.084 | 10.930 | 10.900 | 11.070 | 10.948 |
| uy mean (mm) | 1.524 | 1.470 | 1.480 | 1.670 | 1.451 |
| uy amplitude (mm) | 32.798 | 34.990 | 34.380 | 33.840 | 34.916 |
| uy frequency (Hz) | 5.542 | 5.460 | 5.300 | 5.530 | 5.473 |
| drag mean (N/m) | 458.95 | 460.50 | 457.30 | 459.18 | 460.29 |
| drag amplitude (N/m) | 24.84 | 27.74 | 22.66 | 24.86 | 27.43 |
| drag frequency (Hz) | 11.084 | 10.930 | 10.900 | 11.070 | 10.943 |
| lift mean (N/m) | 1.87 | 2.50 | 2.22 | 1.59 | 2.54 |
| lift amplitude (N/m) | 168.97 | 153.91 | 149.78 | 155.90 | 153.44 |
| lift frequency (Hz) | 5.542 | 5.460 | 5.300 | 5.530 | 5.474 |

