# Sisteama de control de obras civiles


### **Pain Points Actuales en Construcción:**

1. **Desconexión entre oficina y campo**
    - Planos en CAD (coordenadas locales)
    - GPS en obra (WGS84)
    - Levantamientos topográficos (UTM)
    -  Sin sistema unificado
2. **Control de avance ineficiente**
    - Reportes manuales
    - Fotos sin geolocalización precisa
    - Mediciones no verificables
    - Cálculo de volúmenes manual
3. **Problemas de replanteo**
    - Errores de conversión de coordenadas
    - Falta de precisión en GPS comercial
    - Pérdida de tiempo en campo
4. **Gestión de recursos**
    - No saber dónde está cada cuadrilla
    - Materiales sin rastreo preciso
    - Maquinaria subutilizada


```mermaid
graph TB
    %% Estilos
    classDef proyectoStyle fill:#3b82f6,stroke:#2563eb,stroke-width:3px,color:#fff
    classDef elementoStyle fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    classDef reporteStyle fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    classDef cuadrillaStyle fill:#a855f7,stroke:#9333ea,stroke-width:2px,color:#fff
    classDef puntoStyle fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff

    %% Nodos principales
    P[("PROYECTO<br/>───────────<br/>• nombre<br/>• ubicación<br/>• cliente<br/>• presupuesto<br/>• fecha_inicio<br/>• estado")]:::proyectoStyle
    
    E[(" ELEMENTO CONSTRUCTIVO<br/>───────────<br/>• clave<br/>• descripción<br/>• unidad<br/>• cantidad<br/>• elemento_padre")]:::elementoStyle
    
    R[(" REPORTE AVANCE<br/>───────────<br/>• fecha<br/>• porcentaje_avance<br/>• observaciones<br/>• fotos")]:::reporteStyle
    
    C[(" CUADRILLA<br/>───────────<br/>• nombre<br/>• encargado<br/>• especialidad<br/>• num_trabajadores")]:::cuadrillaStyle
    
    PC[(" PUNTO CONTROL<br/>───────────<br/>• nombre<br/>• latitud<br/>• longitud<br/>• descripción")]:::puntoStyle

    %% Relaciones
    P -->|"1:N<br/>tiene"| E
    E -->|"1:N<br/>contiene"| E
    E -->|"1:N<br/>registra"| R
    P -->|"1:N<br/>asigna"| C
    R -.->|"M:N<br/>ejecutan"| C
    E -->|"1:N<br/>ubica"| PC

    %% Notas explicativas
    Note1[" Jerarquía: Los elementos<br/>pueden tener subelementos"]
    Note2[" Muchos a Muchos: Un reporte<br/>puede involucrar varias cuadrillas"]
    Note3[" Geolocalización: Permite<br/>visualización en mapa"]
    
    E -..- Note1
    R -..- Note2
    PC -..- Note3
```
